import json
from src.interface.DataFormat import DataFormat, DataFormatEncoder


def test_DataFormat_append():
    data_format = DataFormat("Testcase", "Execution Time")
    data_format.append("913100-1", "23.063208")
    data_format.append("913100-2", "28.868541")
    assert data_format.x_data == ["913100-1", "913100-2"]
    assert data_format.y_data == ["23.063208", "28.868541"]

def test_DataFormatEncoder_default():
    data_format = DataFormat("Testcase", "Execution Time")
    data_format.append("913100-1", "23.063208")

    encoded_data = DataFormatEncoder().default(data_format)
    expected_data = {
        "x_axis_metadata": "Testcase",
        "y_axis_metadata": "Execution Time",
        "x_data": ["913100-1"],
        "y_data": ["23.063208"]
    }

    assert encoded_data == expected_data

def test_DataFormatEncoder_json_dumps():
    data_format = DataFormat("Testcase", "Execution Time")
    data_format.append("913100-1", "23.063208")

    expected_json = json.dumps({
        "x_axis_metadata": "Testcase",
        "y_axis_metadata": "Execution Time",
        "x_data": ["913100-1"],
        "y_data": ["23.063208"]
    })

    assert DataFormatEncoder().encode(data_format) == expected_json