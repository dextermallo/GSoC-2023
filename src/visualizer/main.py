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
        pass

class Visualizer:
    src_path: str
    parser: argparse.ArgumentParser
    data_groups: UserDict[str, DataGroup]
    figure: plt.Figure
    
    def __init__(self):
        self.src_path = os.getenv("DATA_PATH")
        
        if (self.src_path is None):
            raise Exception("DATA_PATH not set")
        
        self.parser = argparse.ArgumentParser(description='Visualize parsed data')
        self.parser.add_argument('-g', '--group')
        
        self.parser.add_argument('-a', '--add')
        self.parser.add_argument('-rm', '--remove')
        
        self.parser.add_argument('-i', '--info')
        self.parser.add_argument('-d', '--diff', nargs=2, action=TwoArgsAction, help='Two arguments in one variable')
        self.parser.add_argument('-q', '--quit', action='store_true')
        
        self.figure = plt.figure()
        self.data_groups = {}

    # -g <group> -a <data>
    # 540 before 787 after
    # -g 489244 -a cAdvisor.cpu_system_usage
    # -g 489244 -a cAdvisor.cpu_total_usage
    def __add_dataset(self, group: str, add_arg: str):
        if (group is None):
            raise Exception("Group not specified")
        
        if (self.data_groups.get(group) is None):
            self.data_groups[group] = DataGroup(group)
            
        if (self.data_groups[group].data.get(add_arg) is not None):
            logger.warning(f"Data {add_arg} already in group {group}")
            return

        data = self.__load_data(f"{self.src_path}/{group}/{add_arg}.json")
        self.data_groups[group].data[add_arg] = data
    
    def __remove_dataset(self, args):
        pass
    
    def __diff_data_group(self, args):
        pass
         
    def exec(self):
        logger.debug("start exec()")

        while True:
            choice = input("Enter 'q' to quit or 'u' to update the chart: ").split()
            args = self.parser.parse_args(choice)

            if args.add:
                self.__add_dataset(args.group, args.add)
                self.__render_plt(args.group)
            elif args.remove:
                self.__remove_dataset(args)
            elif args.diff:
                self.__diff_data_group(args)
            elif args.group:
                self.__use_group(args)
            elif args.quit:
                break
            else:
                # @TODO: Add help
                continue
        
        plt.close(self.figure)

    def __load_data(self, filename: str) -> List[DataFormat]:
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            logger.error(f"File {filename} not found")
            return None
    
    def __render_plt(self, group: str):
        plt.clf()
    
        for key, value in self.data_groups[group].data.items():
            plt.plot(value["x_data"], value["y_data"], label=key)

        plt.gca().axes.get_xaxis().set_visible(False)
        plt.gca().axes.get_yaxis().set_visible(False)
        plt.xlabel('X')
        plt.ylabel('Y')
        
        # subplot
        # timestamp
        
        plt.title('Dynamic Plot')
        plt.grid(True)
        plt.draw()
        plt.pause(0.1)
    
def main():
    Visualizer().exec()