import docker
import requests
import time
import subprocess
from src.interface.IUtil import IUtil
from src.utils.logger import logger
from src.type import CollectCommandArg, State
from src.utils.utils import container_is_healthy


class CAdvisorUtil(IUtil):
    """_summary_
    CAdvisorCollector is a class for collecting data from cAdvisor API.

    Usage:
    ```sh
    # run the following command, and the data will be stored in $DATA_PATH/<group_id>,
    # once the data is collected, terminate the process with Ctrl+C, and the data will be parsed.
    $ poetry run cadvisor-collector <group_id>
    ```
    """
    
    # @TODO: add to variables
    __waf_container_name: str = "modsec2-apache"

    args: CollectCommandArg
    state: State
    raw_filename: str = "cAdvisor.json"
    
    def collect(self, args: CollectCommandArg, state: State = None):
        logger.debug("start: collect()")
        
        # start cAdvisor container
        self.__start_cadvisor()
        
        # start go-ftw
        proc_ftw_data_collector = subprocess.Popen([f"go-ftw run -d {args.test_cases_dir} -o json"],shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        data_list, timestamp_set = [], set()
        url = f"http://127.0.0.1:8080/api/v1.1/subcontainers/docker/{self.__get_waf_container_id()}"

        # cAdvisor API sends 60 recent dataset,
        # so the data requires to be filtered out duplicates
        while proc_ftw_data_collector.poll() is not None:
            self.fetch_data(data_list, timestamp_set, url)
            time.sleep(15)
        
        self.fetch_data(data_list, timestamp_set, url)
        self._save_json_file(f"{args.raw_output}/{state.name}_{self.raw_filename}", data_list)
        self.__stop_cadvisor()
    
    def report(self):
        pass

    def fetch_data(self, data_list: list, timestamp_set: set, url: str):
        try:
            response = requests.post(url)

            if response.status_code != 200:
                raise Exception("Response status code is not 200")

            for stats in response.json()[0]["stats"]:
                timestamp = stats["timestamp"]
                if timestamp in timestamp_set:
                    continue

                timestamp_set.add(timestamp)
                data_list.append(stats)

            logger.info(f"Data length: {len(data_list)}")
        except Exception as e:
            logger.error(e)

    def __get_waf_container_id(self) -> str:
        """_summary_
        __get_waf_container_id() gets the id of container which name is $__waf_container_name,
        the id is used for cAdvisor API.

        Returns:
            str: waf container id
        """
        logger.debug("start: __get_waf_container_id()")
        client = docker.from_env()
        container = client.containers.get(self.__waf_container_name)
        return container.id
    
    def __start_cadvisor(self):
        logger.info("start: __start_cadvisor()")

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
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
            subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            logger.error(e)
            exit(1)