import subprocess
import os
from src.utils import logger
from src.model.IUtil import IUtil
from src.type import CollectCommandArg, State


class LocustUtil(IUtil):
    """_summary_
    @TODO: documentation
    Args:
        IDataCollector (_type_): _description_

    Raises:
        Exception: _description_
    """
    __exec_filename: str = "exec.py"
    __max_users = 100
    __spawn_rate = 100
    __runtime = 5
    __test_case_per_file_limit = 100

    def collect(self, args: CollectCommandArg, state: State = None):        
        
        self.__exec_filename =os.path.join(args.tmp_dir, self.__exec_filename)
        logger.debug("start: collect()")
        
        # init template
        self.__create_template(args)

        command = f"""locust -f "{self.__exec_filename}" \
                        --headless \
                        -u {self.__max_users} \
                        -r {self.__spawn_rate} \
                        --host={args.waf_endpoint} \
                        --csv={args.raw_output}/{state.name}_locust \
                        -t {self.__runtime}s"""

        _ = subprocess.run(command, shell=True, check=False)
    
    def report(self):
        pass

    # currently, we cannot detect whether the website should block (e.g., 405) or not,
    # because the origin implementation of go-ftw validate the TP/TN by checking logs
    # ideally, this should be validated using outputs
    def __create_template(self, args: CollectCommandArg):
        """
        @TODO: documentation
        """
        data = self._parse_ftw_test_file(args.test_cases_dir, self.__test_case_per_file_limit)
        
        template = """
from locust import HttpUser, task

class AutomatedGenTest(HttpUser):
"""
        
        fn_template = """
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