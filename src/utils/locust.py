import subprocess
import os
import csv
from typing import List
from src.utils import logger, create_data_diff_terminal_table
from src.model.Util import Util
from src.model.ParsedDataItem import ParsedDataItem
from src.type import CollectCommandArg, State, ReportCommandArg


class LocustUtil(Util):
    __exec_filename: str = "exec.py"
    __max_users = 100
    __spawn_rate = 100
    __runtime = 5
    __test_case_per_file_limit = 100
    __raw_file_name = "locust_stats.csv"
    __data_schema = ['type', 'name', 'req_cnt', 'req_fail_cnt', 'median_resp_time', 'avg_resp_time',
                    'min_resp_time', 'max_resp_time', 'avg_content_size', 'req/sec', 'fail/sec', 
                    'p50', 'p66', 'p75', 'p80', 'p90', 'p95', 'p98', 'p99', 'p99.9', 'p99.99', 'p100'
                    ]


    def collect(self, args: CollectCommandArg, state: State = None):    
        self.__exec_filename =os.path.join(args.tmp_dir, self.__exec_filename)

        # init template
        self.__create_template(args)

        command = (
            f"locust -f '{self.__exec_filename}' \\"
            f"--headless \\"
            f"-u {self.__max_users} \\"
            f"-r {self.__spawn_rate} \\"
            f"--host={args.waf_endpoint} \\"
            f"--csv={args.raw_output}/{state.name}_locust \\"
            f"-t {self.__runtime}s"   
        )

        _ = subprocess.run(command, shell=True, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def text_report(self, args: ReportCommandArg):
        before_data = self.__parse_data(os.path.join(f"{args.raw_output}/{State.before.name}_{self.__raw_file_name}"))
        after_data = self.__parse_data(os.path.join(f"{args.raw_output}/{State.after.name}_{self.__raw_file_name}"))
        print(create_data_diff_terminal_table(before_data, after_data, self.__data_schema[2:]))

    def figure_report(self):
        pass

    # currently, we cannot detect whether the website should block (e.g., 405) or not,
    # because the origin implementation of go-ftw validate the TP/TN by checking logs
    # ideally, this should be validated using outputs
    def __create_template(self, args: CollectCommandArg):
        """
        @TODO: documentation
        """
        data = self._parse_ftw_test_file(args.test_cases_dir, self.__test_case_per_file_limit)
        
        template = (
            "from locust import HttpUser, task\n"
            "\n"
            "class AutomatedGenTest(HttpUser):\n"
        )
        
        """
        @task
        def fn$test_title_$stage(self):
            headers = $headers
            data = '''$data'''

            with self.client.$method("/", headers=headers, data=data, catch_response=True) as response:
                try:
                    response.success()
                except Exception as e:
                    response.failure(e)
        """
        fn_template = (
            "\t@task\n"
            "\tdef fn$test_title_$stage(self):\n"
            "\t\theaders = $headers\n"
            "\t\tdata = '''$data'''\n"
            "\n"
            "\t\twith self.client.$method('/', headers=headers, data=data, catch_response=True) as response:\n"
            "\t\t\ttry:\n"
            "\t\t\t\tresponse.success()\n"
            "\t\t\texcept Exception as e:\n"
            "\t\t\t\tresponse.failure(e)\n"
            "\n"
        )

        for d in data:
            for i in range(0, len(d.stages)):
                ctx = fn_template.replace("$test_title", d.test_title.replace("-", "_"))
                ctx = ctx.replace("$stage", str(i))
                ctx = ctx.replace("$headers", str(d.stages[i].headers))
                ctx = ctx.replace("$method", d.stages[i].method.lower())
                ctx = ctx.replace("$data", d.stages[i].data)
                template += ctx
        
        with open(self.__exec_filename, "w") as file:
            file.write(template)
            
    def __parse_data(self, file_path: str)  -> dict[str, List[ParsedDataItem]]:
        res: dict[str, List[ParsedDataItem]] = {
            
        }

        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)

            for i in range(1, len(data)):
                req_type = "Aggregated" if i == len(data) - 1 else data[i][0]
                res[req_type] = [ParsedDataItem(req_type, data[i][2:])]
        return res