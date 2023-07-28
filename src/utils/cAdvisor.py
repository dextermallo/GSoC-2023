import docker
import requests
import time
import subprocess
import json
import os
from typing import List
from src.model.Util import Util
from src.model.Threshold import Threshold
from src.model.ParsedDataItem import ParsedDataItem
from src.type import CollectCommandArg, State, ReportCommandArg
from .fn import container_is_healthy, create_time_series_terminal_plot, save_json
from .logger import logger


class CAdvisorUtil(Util):
    """
    CAdvisorUtil is a class for collecting and analyzing data from cAdvisor API.
    """
    
    # @TODO: add to variables
    __waf_container_name: str = "modsec2-apache"
    raw_filename: str = "cAdvisor.json"
    
    def collect(self, args: CollectCommandArg, state: State = None):
        # start cAdvisor container
        self.__start_cadvisor()
        
        # start go-ftw in parallel
        proc_ftw_data_collector = subprocess.Popen(
            [f"go-ftw run -d {args.test_cases_dir} -o json"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )

        data_list, timestamp_set = [], set()
        url = f"http://127.0.0.1:8080/api/v1.1/subcontainers/docker/{self.__get_waf_container_id()}"

        # cAdvisor API sends 60 recent dataset,
        # so the data requires to be filtered out duplicates
        while proc_ftw_data_collector.poll() is not None:
            self.fetch_data(data_list, timestamp_set, url)
            time.sleep(10)
        
        self.fetch_data(data_list, timestamp_set, url)
        save_json(f"{args.raw_output}/{state.name}_{self.raw_filename}", data_list)
        self.__stop_cadvisor()
    
    def text_report(self, args: ReportCommandArg):
        before_data = self.parse_data(f"{args.raw_output}/{State.before.name}_{self.raw_filename}")
        after_data = self.parse_data(f"{args.raw_output}/{State.after.name}_{self.raw_filename}")
        
        for matrix in ["cpu_total", "cpu_user", "cpu_system", "memory_usage", "memory_cache"]:
            print(create_time_series_terminal_plot(matrix, before_data[matrix], after_data[matrix]))
            
        if not args.threshold_conf:
            return
        
        thresholds: List[Threshold] = self._get_threshold(os.path.join(args.threshold_conf, "cAdvisor.threshold.json"))

        for threshold in thresholds:
            threshold.inspect(before_data[threshold.metric_name], after_data[threshold.metric_name])

    def figure_report(self, args: ReportCommandArg):
        pass

    def parse_data(self, file_path: str)  -> dict[str, List[ParsedDataItem]]:
        res = { "cpu_total": [], "cpu_user": [], "cpu_system": [], "memory_usage": [], "memory_cache": [] }

        with open(file_path, "r") as f:
            raw_data = json.load(f)
            
            for data in raw_data:
                res["cpu_total"].append(ParsedDataItem(data["timestamp"], data["cpu"]["usage"]["total"]))
                res["cpu_user"].append(ParsedDataItem(data["timestamp"], data["cpu"]["usage"]["user"]))
                res["cpu_system"].append(ParsedDataItem(data["timestamp"], data["cpu"]["usage"]["system"]))
                res["memory_usage"].append(ParsedDataItem(data["timestamp"], data["memory"]["usage"]))
                res["memory_cache"].append(ParsedDataItem(data["timestamp"], data["memory"]["cache"]))
            
        return res

    def fetch_data(self, data_list: list, timestamp_set: set, url: str):
        try:
            response = requests.post(url)

            if response.status_code != 200:
                logger.error(f"Response status code is not 200: {response.status_code}")

            for stats in response.json()[0]["stats"]:
                timestamp = stats["timestamp"]
                if timestamp in timestamp_set:
                    continue

                timestamp_set.add(timestamp)
                data_list.append(stats)

            logger.info(f"Current data collected: {len(data_list)}")
        except Exception as e:
            logger.error(e)
            exit(1)

    def __get_waf_container_id(self) -> str:
        """
        __get_waf_container_id() gets the id of container which name is $__waf_container_name,
        the id is used for cAdvisor API.

        Returns:
            str: waf container id
        """
        try:    
            client = docker.from_env()
            container = client.containers.get(self.__waf_container_name)
            return container.id
        except Exception as e:
            logger.error(e)
            exit(1)
    
    def __start_cadvisor(self):
        cmd = """
        docker run \
        --volume=/:/rootfs:ro \
        --volume=/var/run:/var/run:ro \
        --volume=/sys:/sys:ro \
        --volume=/var/lib/docker/:/var/lib/docker:ro \
        --volume=/dev/disk/:/dev/disk:ro \
        --publish=8080:8080 \
        --detach=true \
        --name=cadvisor \
        --privileged \
        --device=/dev/kmsg \
        gcr.io/cadvisor/cadvisor:v0.45.0
        """    
        
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info("Waiting for cAdvisor to be up...")
            cnt = 0
            while not container_is_healthy("cadvisor") and cnt < 6:
                time.sleep(10)
                cnt += 1
            time.sleep(30)
        except Exception as e:
            logger.error(e)
            exit(1)
    
    def __stop_cadvisor(self):
        cmd = "docker stop cadvisor && docker rm cadvisor"
        try:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(e)
            exit(1)