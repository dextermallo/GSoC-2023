import docker
import asciichartpy as asciichart
import dateutil.parser as date_parser
from termcolor import colored
from typing import List
import shutil
from src.model.ParsedDataItem import ParsedDataItem


def container_is_healthy(name_or_id: str):
    return docker.from_env().api.inspect_container(name_or_id)["State"]["Status"] == 'running'

def color_text(text: str, color: str, bold: bool = False):
    return colored(text, color, attrs=[] if not bold else ["bold"])

def get_terminal_column() -> tuple[int, int]:
    return shutil.get_terminal_size((80, 20))

def create_time_series__terminal_plot(
    before_data: List[ParsedDataItem],
    after_data: List[ParsedDataItem],
    terminal_size: tuple[int, int]) -> str:

    column, line = terminal_size

    config = {
        "colors": [ asciichart.blue,  asciichart.red],
        "height": line - 5
    }

    # flatten time series

    def flatten(list: List[ParsedDataItem]):
        start_time = iso_time_str_to_unix_time(list[0].key)
        for i in range(len(list)):
            list[i].key = iso_time_str_to_unix_time(list[i].key) - start_time

    flatten(before_data)
    flatten(after_data)
    
    for i in range(len(before_data)):
        print(before_data[i].key, before_data[i].value)
    
    return ""

def iso_time_str_to_unix_time(iso_time_str: str) -> float:
    return date_parser.parse(iso_time_str).timestamp()