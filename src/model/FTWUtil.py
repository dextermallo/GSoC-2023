import subprocess
import os
import json
import time
from typing import List

from .Util import ParsedDataItem, Util, ReportCommandArg, CollectCommandArg
from src.type import State, Mode


REPORT_PLAIN_TEXT_FORMAT: str = (
    " Test Name: {test_name}\n"
    "       Run: {before_run:12} -> {after_run} ({run_changes})\n"
    "   Success: {before_success:12} -> {after_success} ({success_changes})\n"
    "    Failed: {before_failed:12} -> {after_failed} ({failed_changes})\n"
    "Total Time: {before_total_time:12} -> {after_total_time} ({total_time_changes})\n"
)

class FTWUtil(Util):
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

        # go-ftw requires time to spin up, otherwise the I/O might be timeout
        time.sleep(5)

        # @TODO: better wrapping for different mode
        ftw_util_path = '../ftw' if args.mode == Mode.pipeline.name else 'go-ftw'
        
        output_file = f"{args.raw_output}/{state.name}_{self.raw_filename}"
        # command = f'({ftw_util_path} run -d "{args.test_cases_dir}" -o json > "{output_file}") || echo "some cases failed"'
        command = f'(ls ../ftw  > "{output_file}") || echo "some cases failed"'
        
        proc1 = subprocess.Popen(['ls', '../ftw'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        stdout = proc1.communicate()[0]
        print(stdout)
        
        proc2 = subprocess.Popen(['ls', '../ftw', f" > {output_file}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, check=True)
        stdout2 = proc1.communicate()[0]
        print(stdout2)
        
        # ctx = subprocess.run(command, shell=True, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        # print(ctx.stdout)
        # print(ctx.stderr)
        # print(ctx.returncode)
        # print(output_file)
        # print(command)
    
    def text_report(self, args: ReportCommandArg):
        before_data = self.parse_data(f"{args.raw_output}/{State.before.name}_{self.raw_filename}")
        after_data = self.parse_data(f"{args.raw_output}/{State.after.name}_{self.raw_filename}")

        run_changes = self.create_colored_text_by_value(before_data["run"].value - after_data["run"].value)
        success_changes = self.create_colored_text_by_value(len(before_data["success"]) - len(after_data["success"]))
        failed_changes = self.create_colored_text_by_value(len(before_data["failed"]) - len(after_data["failed"]))
        total_time_changes = self.create_colored_text_by_value(before_data["totalTime"].value - after_data["totalTime"].value)
        
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

        if not args.threshold_conf:
            return

        thresholds = self._get_threshold(os.path.join(args.threshold_conf, "ftw.threshold.json"))

        for threshold in thresholds:
            threshold.inspect(before_data[threshold.metric_name], after_data[threshold.metric_name])

    def figure_report(self, args: ReportCommandArg):
        pass

    def parse_data(self, file_path: str) -> dict[str, List[ParsedDataItem]]:
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
