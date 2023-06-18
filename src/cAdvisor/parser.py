import json
from src.utils.loader import logger
from src.interface.DataFormat import DataFormat, DataFormatEncoder
from typing import List
import os


class CAdvisorDataParser:
    cpu_total_usage: List[DataFormat]
    cpu_user_usage: List[DataFormat]
    cpu_system_usage: List[DataFormat]
    memory_usage: List[DataFormat]
    memory_working_set: List[DataFormat]
    memory_rss: List[DataFormat]
    memory_cache: List[DataFormat]
    src_path: str
    dist_path: str

    def __init__(self, src_path: str, dist_path: str):
        self.cpu_total_usage = []
        self.cpu_user_usage = []
        self.cpu_system_usage = []
        self.memory_usage = []
        self.memory_working_set = []
        self.memory_rss = []
        self.memory_cache = []
        self.src_path = src_path
        self.dist_path = dist_path

    def parse(self):
        logger.debug("start: load_raw_data()")
        with open(self.src_path) as file:
            json_array = json.load(file)
            
            for data in json_array:
                timestamp, cpu_usage, memory = data["timestamp"], data["cpu"]["usage"], data["memory"]
                self.cpu_total_usage.append(DataFormat(timestamp, cpu_usage["total"]))
                self.cpu_user_usage.append(DataFormat(timestamp, cpu_usage["user"]))
                self.cpu_system_usage.append(DataFormat(timestamp, cpu_usage["system"]))
                self.memory_usage.append(DataFormat(timestamp, memory["usage"]))
                self.memory_working_set.append(DataFormat(timestamp, memory["working_set"]))
                self.memory_rss.append(DataFormat(timestamp, memory["rss"]))
            
            self.save_file(f"{self.dist_path}/cpu_total_usage.json", self.cpu_total_usage)
            self.save_file(f"{self.dist_path}/cpu_user_usage.json", self.cpu_user_usage)
            self.save_file(f"{self.dist_path}/cpu_system_usage.json", self.cpu_system_usage)
            self.save_file(f"{self.dist_path}/memory_usage.json", self.memory_usage)
            self.save_file(f"{self.dist_path}/memory_working_set.json", self.memory_working_set)
            self.save_file(f"{self.dist_path}/memory_rss.json", self.memory_rss)
        
    def save_file(self, path: str, data: List[DataFormat]):
        logger.debug("start: save_file()")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w+") as file:
            json.dump(data, file, indent=4, cls=DataFormatEncoder)
        file.close()
    
if __name__ == "__main__":
    CAdvisorDataParser(
        src_path=f"{os.getenv('RAW_DATA_PATH')}/cAdvisor.json", 
        dist_path=os.getenv("PARSED_DATA_PATH")
    ).parse()