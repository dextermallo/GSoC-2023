import subprocess
from argparse import ArgumentParser
from src.utils.logger import logger
from src.interface.IDataCollector import IDataCollector
from src.utils.const import DATA_PATH, FTW_TEST_FILE_PATH, WAF_ENDPOINT


class LocustCollector(IDataCollector):
    """_summary_
    @TODO: documentation
    Args:
        IDataCollector (_type_): _description_

    Raises:
        Exception: _description_
    """
    group_id: str
    test_rule_id: str
    test_file_path: str
    locust_exec_file_path: str
    raw_dist_path: str
    parsed_dist_path: str
    
    __default_host = WAF_ENDPOINT
    host: str
    
    __default_max_users = 100
    max_users: int
    
    __default_spawn_rate = 10
    spawn_rate: int
    
    __default_runtime = 60
    runtime: int
    
    def __init__(self,
                 group_id: str,
                 test_rule_id: str,
                 max_users: int,
                 spawn_rate: int,
                 runtime: int,
                 host: str
                ):
        self.group_id = group_id if group_id is not None else self._generate_group_suffix()
        self.test_rule_id = test_rule_id
        self.max_users = max_users if max_users is not None else self.__default_max_users
        self.spawn_rate = spawn_rate if spawn_rate is not None else self.__default_spawn_rate
        self.runtime = runtime if runtime is not None else self.__default_runtime
        self.host = host if host is not None else self.__default_host
        
        if FTW_TEST_FILE_PATH is None:
            raise Exception("FTW_TEST_FILE_PATH not set")
        
        self.test_file_path = FTW_TEST_FILE_PATH
        self.raw_dist_path = f"{DATA_PATH}/{self.group_id}/"
        self.parsed_dist_path = f"{DATA_PATH}/{self.group_id}/"
        self.locust_exec_file_path = "./exec.py"
        
        super()._create_directory(self.raw_dist_path)
    
    def read_data(self):
        logger.debug("start: read_data()")

        command = f'locust -f "{self.locust_exec_file_path}" \
                        --headless \
                        -u {self.max_users} \
                        -r {self.spawn_rate} \
                        --host={WAF_ENDPOINT} \
                        --csv={self.parsed_dist_path}/{self.group_id} \
                        --headless \
                        -t{self.runtime}'

        _ = subprocess.run(command, shell=True, check=False)       
    
    def save_raw_data(self):
        pass
            
    def parse_data(self):
        """_summary_
        @TODO: implementation
        """
        logger.debug("start: parse_data()")

    # currently, we cannot detect whether the website should block (e.g., 405) or not,
    # because the origin implementation of go-ftw validate the TP/TN by checking logs
    # ideally, this should be validated using outputs
    def create_template(self):
        """
        @TODO: documentation
        """
        data = self._retrieve_rule_test_file_by_id(self.test_rule_id)
        
        template = """
from locust import HttpUser, task, between


class AutomatedGenTest(HttpUser):
    wait_time = between(1, 5)
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
        
        with open(self.locust_exec_file_path, "w") as file:
            file.write(template)

def main():
    """
    @TODO: documentation
    """
    parser = ArgumentParser(add_help=False)
    parser.add_argument("-h", "--host", type=str)
    parser.add_argument("-u", "--users",type=int)
    parser.add_argument("-t", "--run-time", type=int)
    parser.add_argument("-g", "--group-id", type=str)
    parser.add_argument("-id", "--rule-id", type=str)
    parser.add_argument("-r", "----spawn-rate", type=int)
    args = parser.parse_args()
    
    locustCollector = LocustCollector(group_id=args.group_id,
                                      test_rule_id=args.rule_id,
                                      max_users=args.users,
                                      spawn_rate=args.spawn_rate,
                                      runtime=args.run_time,
                                      host=args.host)
    
    locustCollector.create_template()
    locustCollector.read_data()
    # ftw_collector.parse_data()