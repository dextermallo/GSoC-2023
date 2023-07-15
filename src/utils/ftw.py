import subprocess
from src.utils.logger import logger
from src.interface.IUtil import IUtil
from src.type import CommandArg, State


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

    args: CommandArg
    state: State
    raw_filename: str = "ftw.json"

    def __init__(self, args: CommandArg, state: State):
        self.args = args
        self.state = state

    def collect(self):
        logger.debug("start: read_data()")

        # create the directory if not exist, and use go-ftw to run the test
        command = f'go-ftw run -d {self.args.test_cases_dir} -o json > {self.args.raw_output}/{self.state.name}_{self.raw_filename}'
        _ = subprocess.run(command, shell=True, check=False)
    
    def summary():
        pass