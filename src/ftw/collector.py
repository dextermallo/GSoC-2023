import re
import sys
import subprocess
from src.utils.logger import logger
from src.interface.IDataCollector import IDataCollector
from src.interface.DataFormat import DataFormat, DataFormatEncoder
from src.utils.const import DATA_PATH, FTW_TEST_FILE_PATH


class FTWCollector(IDataCollector):
    group_id: str
    test_rule_id: str

    test_file_path: str
    raw_dist_path: str
    parsed_dist_path: str
    
    def __init__(self, group_id: str = None, test_rule_id: str = None):
        self.group_id = group_id if group_id is not None else self._generate_group_suffix()
        self.test_rule_id = test_rule_id
        
        if FTW_TEST_FILE_PATH is None:
            raise Exception("FTW_TEST_FILE_PATH not set")
        
        self.test_file_path = FTW_TEST_FILE_PATH
        self.raw_dist_path = f"{DATA_PATH}/{self.group_id}/ftw.raw.txt"
        self.parsed_dist_path = f"{DATA_PATH}/{self.group_id}"
    
    def read_data(self):
        specify_rule = f'-i {self.test_rule_id}' if self.test_rule_id is not None else ''
        command = f'mkdir -p {self.parsed_dist_path} && \
                    go-ftw run -d {self.test_file_path} {specify_rule} > {self.raw_dist_path}'

        _ = subprocess.run(command, shell=True, check=False)

            
    def save_raw_data(self):
        pass
            
    def parse_data(self):
        logger.debug("start: parse_data()")
        
        rtt = DataFormat("Testcase", "RTT")
        execute_time = DataFormat("Testcase", "Execution Time")
        isSuccess = DataFormat("Testcase", "Success")
        
        pattern = r'running (\w+-\w): (.....\w+) in (\w+.\w+)ms \(RTT (\w+.\w+)ms\)'
        
        with open(self.raw_dist_path, 'r') as file:
            for line in file:
                match = re.search(pattern, line)
                if match:
                    _case, _execute_time, _rtt = match.group(1), match.group(3), match.group(4)
                    _isSuccess = True if 'passed' in match.group(2) else False
                    
                    rtt.append(_case, _rtt)
                    execute_time.append(_case, _execute_time)
                    isSuccess.append(_case, _isSuccess)
                
        super()._save_json_file(f"{self.parsed_dist_path}/ftw.rtt.json", rtt, cls=DataFormatEncoder)
        super()._save_json_file(f"{self.parsed_dist_path}/ftw.execute_time.json", execute_time, cls=DataFormatEncoder)
        super()._save_json_file(f"{self.parsed_dist_path}/ftw.isSuccess.json", isSuccess, cls=DataFormatEncoder)
        
        file.close()

def main():
    group_id = sys.argv[1] if len(sys.argv) > 1 else None
    test_rule_id = sys.argv[2] if len(sys.argv) > 2 else None
    ftw_collector = FTWCollector(group_id=group_id, test_rule_id=test_rule_id)
    ftw_collector.read_data()
    ftw_collector.parse_data()
    