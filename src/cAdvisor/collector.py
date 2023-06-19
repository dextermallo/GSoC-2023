import docker
import requests
import time
import atexit
import os
import json
from src.interface.IDataCollector import IDataCollector
from src.interface.DataFormat import DataFormat, DataFormatEncoder
from src.utils.loader import logger


class CAdvisorCollector(IDataCollector):
    waf_container_name: str
    src_path: str
    raw_dist_path: str
    parsed_dist_path: str
    group_suffix: str
    data_list = []
    

    def __init__(self, waf_container_name: str, src_path: str):
        self.waf_container_name = waf_container_name
        self.src_path = src_path
        self.group_suffix = self._generate_group_suffix()
        self.raw_dist_path = f"{os.getenv('DATA_PATH')}/{self.group_suffix}/cAdvisor.raw.json"
        self.parsed_dist_path = f"{os.getenv('DATA_PATH')}/{self.group_suffix}"
        
        try:
            if self.raw_dist_path is None:
                raise Exception("RAW_DATA_PATH is not defined")
            if self.parsed_dist_path is None:
                raise Exception("PARSED_DATA_PATH is not defined")
        except Exception as e:
            logger.error(e)
            exit(1)
        
    def read_data(self):
        logger.debug("start: read_data()")
        # cAdvisor API sends 60 recent dataset, so the data requires to be filtered out duplicates
        timestamp_set = set()
        url = f"{self.src_path}/api/v1.1/subcontainers/docker/{self.__get_waf_container_id()}"

        while True:
            try:
                response = requests.post(url)

                if response.status_code != 200:
                    raise Exception("Response status code is not 200")

                for stats in response.json()[0]["stats"]:

                    timestamp = stats["timestamp"]
                    if timestamp in timestamp_set:
                        continue

                    timestamp_set.add(timestamp)
                    self.data_list.append(stats)
                
                logger.info(f"Data length: {len(self.data_list)}")
            except Exception as e:
                logger.error(e)
                break

            time.sleep(15)

    def save_raw_data(self):
        logger.debug("start: save_raw_data()")
        super()._save_json_file(self.raw_dist_path, self.data_list)
    
    def __get_waf_container_id(self) -> str:
        logger.debug("start: __get_waf_container_id()")
        client = docker.from_env()
        container = client.containers.get(self.waf_container_name)
        return container.id
    
    def parse_data(self):        
        logger.debug("start: parse_data()")

        self.save_raw_data()

        cpu_total_usage = DataFormat("timestamp", "cpu_total_usage")
        cpu_user_usage = DataFormat("timestamp", "cpu_user_usage")
        cpu_system_usage = DataFormat("timestamp", "cpu_system_usage")
        memory_usage = DataFormat("timestamp", "memory_usage")
        memory_working_set = DataFormat("timestamp", "memory_working_set")
        memory_rss = DataFormat("timestamp", "memory_rss")
        
        with open(self.raw_dist_path) as file:
            json_array = json.load(file)
            
            for data in json_array:
                timestamp, cpu_usage, memory = data["timestamp"], data["cpu"]["usage"], data["memory"]
                
                cpu_total_usage.append(timestamp, cpu_usage["user"])
                cpu_user_usage.append(timestamp, cpu_usage["user"])
                cpu_system_usage.append(timestamp, cpu_usage["system"])
                memory_usage.append(timestamp, memory["usage"])
                memory_working_set.append(timestamp, memory["working_set"])
                memory_rss.append(timestamp, memory["rss"])
            
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.cpu_total_usage.json", cpu_total_usage, cls=DataFormatEncoder)
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.cpu_user_usage.json", cpu_user_usage, cls=DataFormatEncoder)
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.cpu_system_usage.json", cpu_system_usage, cls=DataFormatEncoder)
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.memory_usage.json", memory_usage, cls=DataFormatEncoder)
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.memory_working_set.json", memory_working_set, cls=DataFormatEncoder)
            super()._save_json_file(f"{self.parsed_dist_path}/cAdvisor.memory_rss.json", memory_rss, cls=DataFormatEncoder)


def main():
    cAdvisor = CAdvisorCollector(
        os.getenv("WAF_CONTAINER_NAME"),
        os.getenv("CADVISOR_ENDPOINT")
    )

    atexit.register(cAdvisor.parse_data)
    cAdvisor.read_data()