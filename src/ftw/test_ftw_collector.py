import pytest
import json
import os
import shutil
from src.ftw.collector import FTWCollector
from src.utils.const import DATA_PATH


@pytest.fixture
def ftw_collector(scope='session', autouse=True):
    group_id = "ftw_test_group_id"
    test_rule_id = "920170"
    yield FTWCollector(group_id, test_rule_id)

def test_collector_gen_group_id():
    new_collector = FTWCollector()
    # new_collector.group_id should be a six-digit string
    assert isinstance(new_collector.group_id, str)
    assert len(new_collector.group_id) == 6
    assert new_collector.group_id.isdigit()
        
def test_collector_proc(ftw_collector: FTWCollector):
    ftw_collector.read_data()
    # check if file is exists
    assert os.path.exists(ftw_collector.raw_dist_path)
    
    # check the file starts with go-ftw prefix
    with open(ftw_collector.raw_dist_path, 'r') as file:
        ctx = file.read()
        assert "Running go-ftw!" in ctx
        
    ftw_collector.parse_data()
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.rtt.json")
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.execute_time.json")
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.isSuccess.json")
    
    # clean up
    shutil.rmtree(f"{DATA_PATH}/{ftw_collector.group_id}")
    
def test_parse_data(ftw_collector: FTWCollector):
    ctx = """
    👉 executing tests in file 913100.yaml
	running 913100-1: ✔ passed in 23.063208ms (RTT 61.146959ms)
	running 913100-2: ✔ passed in 28.868541ms (RTT 67.045042ms)
	running 913100-3: 💥 failed in 27.536042ms (RTT 61.949459ms)
    👉 executing tests in file 913101.yaml
	running 913101-1: 💥 failed in 21.570708ms (RTT 58.723167ms)
	running 913101-2: ✔ passed in 23.023958ms (RTT 57.584209ms)
    👉 executing tests in file 913102.yaml
	running 913102-1: 💥 failed in 27.753042ms (RTT 62.830584ms)
    """
    
    # save ctx to a tmp file in pytest and parse it
    ftw_collector._save_file(ftw_collector.raw_dist_path, ctx)
    
    ftw_collector.parse_data()
    
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.rtt.json")
    expected_rtt_data = {
        "x_axis_metadata": "Testcase",
        "y_axis_metadata": "RTT",
        "x_data": [
            "913100-1",
            "913100-2",
            "913100-3",
            "913101-1",
            "913101-2",
            "913102-1"
        ],
        "y_data": [
            "61.146959",
            "67.045042",
            "61.949459",
            "58.723167",
            "57.584209",
            "62.830584"
        ]
    }
    
    with open(f"{ftw_collector.parsed_dist_path}/ftw.rtt.json") as file:
        assert json.load(file) == expected_rtt_data
    file.close()
    
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.execute_time.json")
    expected_execution_time_data = {
        "x_axis_metadata": "Testcase",
        "y_axis_metadata": "Execution Time",
        "x_data": [
            "913100-1",
            "913100-2",
            "913100-3",
            "913101-1",
            "913101-2",
            "913102-1"
        ],
        "y_data": [
            "23.063208",
            "28.868541",
            "27.536042",
            "21.570708",
            "23.023958",
            "27.753042"
        ]
    }
    
    with open(f"{ftw_collector.parsed_dist_path}/ftw.execute_time.json") as file:
        assert json.load(file) == expected_execution_time_data
    file.close()
    
    assert os.path.exists(f"{ftw_collector.parsed_dist_path}/ftw.isSuccess.json")
    expected_is_success_data = {
        "x_axis_metadata": "Testcase",
        "y_axis_metadata": "Success",
        "x_data": [
            "913100-1",
            "913100-2",
            "913100-3",
            "913101-1",
            "913101-2",
            "913102-1"
        ],
        "y_data": [
            True,
            True,
            False,
            False,
            True,
            False
        ]
    }
    
    with open(f"{ftw_collector.parsed_dist_path}/ftw.isSuccess.json") as file:
        assert json.load(file) == expected_is_success_data
    file.close()    
    
    # clean up
    shutil.rmtree(f"{DATA_PATH}/{ftw_collector.group_id}")