import os
import json
import pytest
import signal
import shutil
from src.cAdvisor.collector import CAdvisorCollector
from src.utils.const import DATA_PATH


@pytest.fixture
def cadvisor_collector(scope='session', autouse=True):
    group_id = "test_cadvisor_group"
    yield CAdvisorCollector(group_id)
    
def test_collector_proc(cadvisor_collector):

    def test_read_data():
        def timeout_handler(signum, frame):
            raise TimeoutError("read_data execution timed out")
        
        with pytest.raises(TimeoutError):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(5)
            cadvisor_collector.read_data()

        signal.alarm(0)
    
    def test_save_raw_data():
        cadvisor_collector.save_raw_data()
        assert os.path.exists(cadvisor_collector.raw_dist_path)
        with open(cadvisor_collector.raw_dist_path, "r") as file:
            saved_data = json.load(file)
            assert isinstance(saved_data, list)
            assert len(saved_data) > 0

    def __verify_parsed_json_file(matrix: str, x_data_type: type, y_data_type: type):
        file_path = os.path.join(cadvisor_collector.parsed_dist_path, f"cAdvisor.{matrix}.json")
        
        assert os.path.exists(file_path)

        with open(file_path, 'r') as file:
            data = json.load(file)
            
            assert data["x_axis_metadata"] == "timestamp"
            assert data["y_axis_metadata"] == matrix
            
            assert isinstance(data["x_data"], list)
            assert all(isinstance(item, x_data_type) for item in data["x_data"])
            assert isinstance(data["y_data"], list)
            assert all(isinstance(item, y_data_type) for item in data["y_data"])

    def test_parse_data():
        cadvisor_collector.parse_data()
        __verify_parsed_json_file("cpu_total_usage", str, int)
        __verify_parsed_json_file("cpu_user_usage", str, int)
        __verify_parsed_json_file("cpu_system_usage", str, int)
        __verify_parsed_json_file("memory_usage", str, int)
        __verify_parsed_json_file("memory_working_set", str, int)
        __verify_parsed_json_file("memory_rss", str, int)
         
    test_read_data()
    test_save_raw_data()
    test_parse_data()
    
    # clean up
    shutil.rmtree(f"{DATA_PATH}/{cadvisor_collector.group_id}")