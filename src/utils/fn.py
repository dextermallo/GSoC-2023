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
    return 

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