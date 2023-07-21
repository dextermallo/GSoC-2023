import docker
import asciichartpy as asciichart
import dateutil.parser as date_parser
from astropy.table import Table
from termcolor import colored
from typing import Type, List
import json
import shutil
import os
from src.model.ParsedDataItem import ParsedDataItem
from .logger import logger


def container_is_healthy(name_or_id: str):
    return docker.from_env().api.inspect_container(name_or_id)["State"]["Status"] == 'running'

def color_text(text: str, color: str, bold: bool = False):
    return colored(text, color, attrs=[] if not bold else ["bold"])

def create_time_series_terminal_plot(
    title: str,
    before_data: List[ParsedDataItem],
    after_data: List[ParsedDataItem]) -> str:

    (column, line) = shutil.get_terminal_size((80, 20))
    
    if column < 120:
        raise Exception("Terminal column is too small, minimum requirement: 120")
    
    if line < 12:
        raise Exception("Terminal line is too small, minimum requirement: 12")

    config = {
        "colors": [ asciichart.blue,  asciichart.red],
        "height": line - 7
    }

    # flatten time series
    def flatten(list: List[ParsedDataItem]) -> list:
        start_time = iso_time_str_to_unix_time(list[0].key)
        end_time = iso_time_str_to_unix_time(list[-1].key)
        for i in range(len(list)):
            compressed_time = (iso_time_str_to_unix_time(list[i].key) - start_time) / (end_time - start_time)
            list[i].key = round(compressed_time * 100)

        arr, cur = [], 0

        # filled
        for i in range(100):
            if cur >= len(list):
                arr.append(arr[-1])
            if list[cur].key == i:
                arr.append(list[cur].value)
                cur += 1
            else:
                arr.append(arr[-1])
        return arr

    f_before, f_after = flatten(before_data), flatten(after_data)

    # create title line
    spacer = (column - len(title) - 4) // 2
    title_line = "=" * spacer + f"  {title}  " + "=" * spacer

    return (
        f"{color_text(title_line, 'white', True)}\n" +
        f"{color_text('Warning: The text-chart only provides a simple visualization and it cannot depict the details.', 'yellow')}" +
        f"{color_text('Please use --format figure for better view. ', 'yellow')}" +
        f"({color_text('Before: Blue', 'blue')} / {color_text('After: Red', 'red')})\n\n" +
        asciichart.plot([f_before, f_after], config)
    )

def iso_time_str_to_unix_time(iso_time_str: str) -> float:
    return date_parser.parse(iso_time_str).timestamp()

def create_directory(dist_path: str):
    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    
def save_file(dist_path: str, data: str):
    """_summary_

    Args:
        dist_path (str): _description_
        data (str): _description_

    Returns:
        _type_: _description_
    """

    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    with open(dist_path, "w+") as file:
        file.write(data)
    file.close()

def save_json(dist_path: str, data: any, cls: Type[json.JSONEncoder] = None):
    """_summary_

    Args:
        dist_path (str): _description_
        data (any): _description_
        cls (Type[json.JSONEncoder], optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """

    os.makedirs(os.path.dirname(dist_path), exist_ok=True)
    with open(dist_path, "w+") as file:
        json.dump(data, file, indent=2, cls=cls)
    file.close()
    
def create_colored_text_by_value(value: any) -> str:
    color: str

    if type(value) == bool:
        color = "green" if value else "red"
    elif type(value) == float or type(value) == int:
        if value == 0:
            color = "light_grey"
        elif value > 0:
            color = "red"
            value = f"+{value}"
        else:
            color = "green"
    else:
        raise Exception("Invalid value type")

    return colored(str(value),color, attrs=["bold"])

# @TODO: make it generic
def create_data_diff_terminal_table(before_data: dict[str, List[ParsedDataItem]],
                                    after_data: dict[str, List[ParsedDataItem]],
                                    row: List[str]) -> Table:

    key_set = set(before_data.keys())

    if before_data.keys() != after_data.keys():
        logger.error("The before and after data must have the same keys. The report will only show the shared keys.")
        key_set = [k for k in after_data.keys() if k in key_set]

    output = Table()
    output['Matrix'] = row

    for key in key_set:
        before, after, cur_output = before_data[key], after_data[key], []
        
        if len(before[0].value) != len(after[0].value):
            raise Exception("The before and after data must have the same length")
        
        for i in range(len(before[0].value)):
            diff = round(float(before[0].value[i]) - float(after[0].value[i]), 4)
            out = (
                f"{'{0:.4f}'.format(float(before[0].value[i]))}" +
                f" ({create_colored_text_by_value(diff)})"
            )
            cur_output.append(out)
    
        output[key] = cur_output    
    return output