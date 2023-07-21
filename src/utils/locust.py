import subprocess
import os
from src.utils import logger
from src.model.Util import Util
from src.type import CollectCommandArg, State


class LocustUtil(Util):
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
    
    def text_report(self):
        pass

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