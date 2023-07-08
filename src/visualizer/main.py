import matplotlib.pyplot as plt
import json
import argparse
import os
from datetime import datetime
from typing import List
from collections import UserDict
from src.interface.DataFormat import DataFormat
from src.utils.logger import logger
from src.utils.const import DATA_PATH


class DataGroup:
    group_id: str
    data: UserDict[str, DataFormat]
    
    def __init__(self, group_id: str) -> None:
        self.group_id = group_id
        self.data = {}

class Visualizer:
    src_path: str
    parser: argparse.ArgumentParser
    data_groups: UserDict[str, DataGroup]
    data_length: int
    figure: plt.Figure
    
    def __init__(self):
        self.src_path = DATA_PATH
        
        if (self.src_path is None):
            raise Exception("DATA_PATH not set")
        
        self.parser = argparse.ArgumentParser(description='Visualize parsed data')
        
        subparsers = self.parser.add_subparsers(dest='command')
        
        add_group_parser = subparsers.add_parser('add-group')
        add_group_parser.add_argument('group_id', type=str)
        add_group_parser.add_argument('-c', '--compress-time', action='store_true')
        
        remove_group_parser = subparsers.add_parser('remove-group')
        remove_group_parser.add_argument('group_id', type=str)
        
        subparsers.add_parser('info')
        subparsers.add_parser('quit')

        self.figure = None
        self.data_groups = {}
        self.data_length = 0

    def __add_group(self, group: str):
        if (group is None):
            raise Exception("Group not specified")
        
        if (self.data_groups.get(group) is None):
            self.data_groups[group] = DataGroup(group)
        
        files = os.listdir(f"{self.src_path}/{group}")
        data_len_cnt = 0
        for file in files:
            if (self.data_groups[group].data.get(file) is not None):
                logger.warning(f"Data {file} already in group {group}")
                continue
                    
            # skip raw data
            if file.find("raw") != -1:
                continue
                    
            data = self.__load_data(f"{self.src_path}/{group}/{file}")
            self.data_groups[group].data[file] = data
            data_len_cnt += 1
        
        self.data_length = data_len_cnt

    
    """
    @TODO: impl
    """
    def __remove_group(self, group: str):
        pass
    
    def exec(self):
        logger.debug("start exec()")

        while True:
            choice = input("Enter 'q' to quit or 'u' to update the chart: ").split()
            args = self.parser.parse_args(choice)

            if args.command == "add-group":
                self.__add_group(args.group_id)
                self.__render_plt(args.compress_time)
            elif args.command == "remove-group":
                self.__remove_group(args.group_id)
            elif args.command == "info":
                continue
            elif args.command == "quit":
                break
            else:
                continue
        
        plt.close('all')

    def __load_data(self, filename: str) -> List[DataFormat]:
        logger.debug(f"start: __load_data({filename})")
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            return None
    
    def __render_plt(self, compress_time: bool):
        logger.debug(f"start: __render_plt()")

        plt.close('all')

        self.fig, axes = plt.subplots(self.data_length, sharex=True)
        plt.subplots_adjust(hspace=0.5, wspace=0.5)
        self.fig.set_figheight(6)
        self.fig.set_figwidth(10)

        colors = ["red", "blue", "green"]
        
        for group_id in self.data_groups.keys():
            idx, used_color = 0, colors.pop()

            for key, value in self.data_groups[group_id].data.items():
                if compress_time:
                    axes[idx].plot(self.__standardize_timestamp(value["x_data"]),
                                   value["y_data"],
                                   color=used_color,
                                   label=group_id,
                                   marker='o',
                                   markersize=2.5
                    )
                else:
                    axes[idx].plot(value["x_data"],
                                   value["y_data"],
                                   color=used_color,
                                   label=group_id,
                                   marker='o',
                                   markersize=2.5
                    )
                axes[idx].set_title(key)
                axes[idx].set_xticks([])
                axes[idx].set_yticks([])
                axes[idx].grid(True)
                axes[idx].xaxis.set_major_locator(plt.MaxNLocator(3))
                axes[idx].yaxis.set_major_locator(plt.MaxNLocator(3))
                idx += 1
        
        plt.ylim(top=plt.yticks()[0][-1])
        plt.legend()
        plt.draw()
        plt.tight_layout(pad=1.5)
        plt.pause(0.1)

    def __standardize_timestamp(self, timestamp_list: List[str]) -> List[int]:
        unix_t_list = [self.__str_iso8601_to_unix(timestamp) for timestamp in timestamp_list]
        min_t, max_t = unix_t_list[0], unix_t_list[-1]
        
        res = []
        
        for t in unix_t_list:
            res.append((t - min_t) / (max_t - min_t))
        
        return res
    
    def __str_iso8601_to_unix(self, s: str) -> int:
        date_part, time_part = s.split('T')
        time_part, _ = time_part.split('Z')
        date_components = list(map(int, date_part.split('-')))
        time_components = list(map(float, time_part.split(':')))
        seconds = int(time_components[2])
        microseconds = int((time_components[2] - seconds) * 1e6)

        # Create a datetime object
        dt = datetime(
            date_components[0],
            date_components[1],
            date_components[2],
            int(time_components[0]),
            int(time_components[1]),
            seconds,
            microseconds
        )
        
        return dt.timestamp()

def main():
    plt.set_loglevel('WARNING')
    Visualizer().exec()