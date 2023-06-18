import docker
import requests
from src.interface.IDataCollector import IDataCollector
import time
import json
import atexit
import os
from src.utils.loader import logger


class CAdvisorCollector(IDataCollector):
    waf_container_name: str
    src_path: str
    dist_path: str
    data_list = []

    def __init__(self, waf_container_name: str, src_path: str, dist_path: str):
        self.waf_container_name = waf_container_name
        self.src_path = src_path
        self.dist_path = dist_path
        
    def read_data(self):
        logger.debug("start: read_data()")
        # cAdvisor API sends 60 recent dataset, so the data requires to be filtered out duplicates
        timestamp_set = set()
        url = f"{self.src_path}/api/v1.1/subcontainers/docker/{self._get_waf_container_id()}"

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

    def store_raw_data(self):
        logger.debug("start: store_raw_data()")
        
        dist_path = f"{self.dist_path}/cAdvisor.json"
        os.makedirs(os.path.dirname(dist_path), exist_ok=True)
        with open(dist_path, "w+") as file:
            json.dump(self.data_list, file, indent=4)
        file.close()
    
    def _get_waf_container_id(self) -> str:
        logger.debug("start: _get_waf_container_id()")
        client = docker.from_env()
        container = client.containers.get(self.waf_container_name)
        return container.id

if __name__ == "__main__":    
    cAdvisor = CAdvisorCollector(
        os.getenv("WAF_CONTAINER_NAME"),
        os.getenv("CADVISOR_ENDPOINT"),
        os.getenv("RAW_DATA_PATH")
    )
    
    atexit.register(cAdvisor.store_raw_data)
    cAdvisor.read_data()