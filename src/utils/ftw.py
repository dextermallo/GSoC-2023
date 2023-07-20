import subprocess
import os
import json
from typing import List
from src.utils import logger, color_text
from src.model.IUtil import IUtil, Threshold
from src.model.ParsedDataItem import ParsedDataItem
from src.type import CollectCommandArg, State, ReportCommandArg, ReportFormat



REPORT_PLAIN_TEXT_FORMAT: str = (
    "Test Name: {test_name}\n",
    "Run: {before_run} -> {after_run} ({run_changes})\n",
    "Success: {before_success} -> {after_success} ({success_changes})",
    "Failed: {before_failed} -> {after_failed} ({failed_changes})",
    "Total Time: {before_total_time} -> {after_total_time} ({total_time_changes})"
)

class FTWUtil(IUtil):
    """_summary_
    FTWCollector is a class for collecting data from go-ftw, it utilizes the go-ftw
    for calling the testcases and parsing the data.

    Usage:
        ```sh
        # both group_id and test_rule_id are optional,
        # if group_id is not specified, it will be generated automatically with a
        # six-digit random number.
        # if test_rule_id is not specified, it will run all testcases.
        $ poetry run ftw-collector <group_id> <test_rule_id>
        ```
    """

    raw_filename: str = "ftw.json"

    def collect(self, args: CollectCommandArg, state: State = None):
        logger.debug("start: read_data()")

        # create the directory if not exist, and use go-ftw to run the test
        command = f'go-ftw run -d {args.test_cases_dir} -o json > {args.raw_output}/{state.name}_{self.raw_filename}'
        _ = subprocess.run(command, shell=True, check=False)
    
    def report(self, args: ReportCommandArg):
        logger.debug("start: report()")

        # get data
        before_data = self.parse_data(f"{args.raw_output}/{State.before.name}_{self.raw_filename}")
        after_data = self.parse_data(f"{args.raw_output}/{State.after.name}_{self.raw_filename}")

        # get threshold
        thresholds: List[Threshold] = []
        
        if args.threshold_conf:    
            thresholds = self._get_threshold(os.path.join(args.threshold_conf, "ftw.threshold.json"))
        
        if args.format == ReportFormat.text:

            run_changes = self._create_colored_text_by_value(before_data["run"].value - after_data["run"].value)
            success_changes = self._create_colored_text_by_value(len(before_data["success"]) - len(after_data["success"]))
            failed_changes = self._create_colored_text_by_value(len(before_data["failed"]) - len(after_data["failed"]))
            total_time_changes = self._create_colored_text_by_value(before_data["totalTime"].value - after_data["totalTime"].value)
            
            # generate report
            report = REPORT_PLAIN_TEXT_FORMAT.format(
                test_name=args.test_name,
                before_run=before_data["run"].value,
                after_run=after_data["run"].value,
                run_changes=run_changes,
                before_success=len(before_data["success"]),
                after_success=len(after_data["success"]),
                success_changes=success_changes,
                before_failed=len(before_data["failed"]),
                after_failed=len(after_data["failed"]),
                failed_changes=failed_changes,
                before_total_time=before_data["totalTime"].value,
                after_total_time=after_data["totalTime"].value,
                total_time_changes=total_time_changes
            )
            
            print(report)
            # evaluate threshold

            for threshold in thresholds:
                if not threshold.isPassed(before_data[threshold.metric_name], after_data[threshold.metric_name]):
                    print((f"Threshold: {threshold.threshold_name:24} {color_text('failed', 'red', True)}"))
                else:    
                    print((f"Threshold: {threshold.threshold_name:24} {color_text('passed', 'green', True)}"))

    def parse_data(self, file_path: str) -> dict:
        logger.debug("start: parse_data()")
        # read the raw data from the file
        res = {}
        
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
            
            # parse "run"
            res["run"] = ParsedDataItem('run', raw_data['run'], [])
            
            # parse "success"
            res["success"] = []
            for rule in raw_data["success"]:
                res["success"].append(ParsedDataItem("caseID", rule, [rule]))

            # parse "failed"
            res["failed"] = []
            for rule in raw_data["failed"]:
                res["failed"].append(ParsedDataItem("caseID", rule, [rule]))
            
            # parse "skipped"
            res["skipped"] = []
            for rule in raw_data["skipped"]:
                res["skipped"].append(ParsedDataItem("caseID", rule, [rule]))
            
            # parse "runtime"
            res["runtime"] = []
            for rule in raw_data["runtime"]:
                res["runtime"].append(ParsedDataItem(rule, raw_data["runtime"][rule], [rule, rule.split("-")[0]]))
            
            # parse "totalTime"
            res["totalTime"] = ParsedDataItem("TotalTime", raw_data["TotalTime"], [])

        return res
