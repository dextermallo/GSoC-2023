import json
import argparse
import matplotlib.pyplot as plt
from datetime import datetime
from src.utils.loader import logger
from typing import List
from collections import UserDict
from src.interface.DataFormat import DataFormat
import os


class TwoArgsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values[:2])  # Store the first two arguments as a list

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
        self.src_path = os.getenv("DATA_PATH")
        
        if (self.src_path is None):
            raise Exception("DATA_PATH not set")
        
        self.parser = argparse.ArgumentParser(description='Visualize parsed data')
        
        subparsers = self.parser.add_subparsers(dest='command')
        
        add_group_parser = subparsers.add_parser('add-group')
        add_group_parser.add_argument('group_id', type=str)
        
        remove_group_parser = subparsers.add_parser('remove-group')
        remove_group_parser.add_argument('group_id', type=str)
        
        subparsers.add_parser('info')
        subparsers.add_parser('quit')
        
        self.figure = plt.figure()
        self.data_groups = {}
        self.data_length = 0

    # -g <group> -a <data>
    # 540 before 787 after
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

    
    def __remove_group(self, group: str):
        pass
    
    def exec(self):
        logger.debug("start exec()")

        while True:
            choice = input("Enter 'q' to quit or 'u' to update the chart: ").split()
            args = self.parser.parse_args(choice)


            if args.command == "add-group":
                self.__add_group(args.group_id)
                self.__render_plt()
            elif args.command == "remove-group":
                self.__remove_group(args.group_id)
            elif args.command == "info":
                continue
            elif args.command == "quit":
                break
            else:
                continue
        
        plt.close(self.figure)

    def __load_data(self, filename: str) -> List[DataFormat]:
        logger.debug(f"start: __load_data({filename})")
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            return None
    
    def __render_plt(self):
        logger.debug(f"start: __render_plt()")

        plt.clf()
        self.fig, axes = plt.subplots(self.data_length)
        plt.subplots_adjust(hspace=None)
        self.fig.tight_layout()
        
        colors = ["red", "blue", "green"]
        
        for group_id in self.data_groups.keys():
            idx, used_color = 0, colors.pop()

            for key, value in self.data_groups[group_id].data.items():
                axes[idx].plot(self.__standardize_timestamp(value["x_data"]), value["y_data"], color=used_color)
                axes[idx].set_title(key)
                axes[idx].set_xticks([])
                axes[idx].set_yticks([])
                idx += 1
        
        plt.draw()
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
            date_components[0],  # year
            date_components[1],  # month
            date_components[2],  # day
            int(time_components[0]),  # hour
            int(time_components[1]),  # minute
            seconds,
            microseconds
        )
        
        return dt.timestamp()

def main():
    Visualizer().exec()