import os
import json
from src.interface.IUtil import DataFormat
from IUtil import IDataCollector


class MockDataCollector(IDataCollector):
    def __init__(self):
        pass

    def read_data(self):
        pass

    def save_raw_data(self):
        pass

    def parse_data(self):
        pass

def test_save_file(tmpdir):
    collector = MockDataCollector()
    dist_path = os.path.join(tmpdir, "test.txt")
    data = "test data for plain text"

    collector._save_file(dist_path, data)

    assert os.path.exists(dist_path)

    with open(dist_path, "r") as file:
        saved_data = file.read()
        assert saved_data == data

def test_save_json_file(tmpdir):
    collector = MockDataCollector()
    dist_path = os.path.join(tmpdir, "test.json")
    data = { "test": "case" }

    collector._save_json_file(dist_path, data)

    assert os.path.exists(dist_path)
    with open(dist_path, "r") as file:
        saved_data = json.load(file)
        assert saved_data == data

def test_is_validate_data_format():
    collector = MockDataCollector()
    valid_data = DataFormat("x-axis", "y-axis")
    invalid_data = { "x": "y" }

    assert collector._is_validate_data_format(valid_data) is True
    assert collector._is_validate_data_format([valid_data, valid_data]) is True
    assert collector._is_validate_data_format(invalid_data) is False
    assert collector._is_validate_data_format([valid_data, invalid_data]) is False

def test_generate_group_suffix():
    collector = MockDataCollector()
    suffix = collector._generate_group_suffix()
    assert isinstance(suffix, str)
    assert len(suffix) == 6