import docker
import requests
import time
import atexit
import sys
import json
from src.interface.IDataCollector import IDataCollector
from src.interface.DataFormat import DataFormat, DataFormatEncoder
from src.utils.logger import logger
from src.utils.const import DATA_PATH, WAF_CONTAINER_NAME, CADVISOR_ENDPOINT


class CAdvisorCollector(IDataCollector):
    """_summary_
    CAdvisorCollector is a class for collecting data from cAdvisor API.

    Usage:
    ```sh
    # run the following command, and the data will be stored in $DATA_PATH/<group_id>,
    # once the data is collected, terminate the process with Ctrl+C, and the data will be parsed.
    $ poetry run cadvisor-collector <group_id>
    ```
    """    
    waf_container_name: str
    src_path: str
    raw_dist_path: str
    parsed_dist_path: str
    group_id: str
    data_list = []

    def __init__(self, group_id: str):
        self.waf_container_name = WAF_CONTAINER_NAME
        self.src_path = CADVISOR_ENDPOINT
        self.group_id = group_id if group_id is not None else self._generate_group_id()
        self.raw_dist_path = f"{DATA_PATH}/{self.group_id}/cAdvisor.raw.json"
        self.parsed_dist_path = f"{DATA_PATH}/{self.group_id}"
        
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
        """_summary_
        __get_waf_container_id() gets the id of container which name is $WAF_CONTAINER_NAME,
        the id is used for cAdvisor API.

        Returns:
            str: waf container id
        """
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

        file.close()

def main():
    cAdvisor_collector = CAdvisorCollector(sys.argv[1])
    atexit.register(cAdvisor_collector.parse_data)
    cAdvisor_collector.read_data()