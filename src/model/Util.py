import yaml
import os
import json
from abc import ABC, abstractmethod
from typing import List
from src.utils import logger
from .Threshold import Threshold
from src.type import ReportCommandArg, CollectCommandArg
from termcolor import colored


class _FTWTestInput:
    method: str = "GET"
    port: int = 80
    headers: dict = {}
    data: str = ""
    uri: str = "/"
    
    def __init__(self, dict: dict):
        for k, v in dict.items():
            setattr(self, k, v)
        
        HTTP_METHOD_LIST = ["GET", "HEAD", "POST", "PUT", "DELETE"
                            , "OPTIONS", "TRACE", "PATCH"]
        
        if self.method not in HTTP_METHOD_LIST:
            logger.error(f"Invalid method: {self.method}, replace for 'GET to bypass'")
            self.method = "GET"

class _FTWTestSchema:
    test_title: str
    stages: List[_FTWTestInput]
    
    def __init__(self, test_title: str, stages: List[_FTWTestInput]):
        self.test_title = test_title
        self.stages = stages

class Util(ABC):
    """_summary_
    Util is an abstract class for Utils,
    it is used to read data from a source and store it in a database.
    extend this class to implement your own data collector.
    
    Generally, a collector perform the following steps in linear order:
    read_data() -> save_raw_data() -> parse_data()
    
    Noted that read_data() and save_raw_data() are optional if the raw data sources
    are provided. In this case, the data can be parsed directly.
    """

    @abstractmethod
    def collect(self, args: CollectCommandArg):
        """_summary_
        read_data() is a method for reading data from a source.
        It is an optional func to be implemented if the data source 
        (e.g., raw datafile like logs) is already provided.
        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError
    
    @abstractmethod
    def text_report(self, args: ReportCommandArg):
        """_summary_
        save_raw_data() is a method for saving raw data to a file.
        It follows the func read_data() and is used to save the data, and it 
        is an optional func to be implemented if the data source is already provided.

        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError

    @abstractmethod
    def figure_report(self, args: ReportCommandArg):
        raise NotImplementedError
       
    def _parse_ftw_test_file(self, file_path: str, case_limit: int) -> List[_FTWTestSchema]:
        logger.debug('start: _parse_ftw_test_file()')

        if file_path is None:
            raise Exception("file_path is None")
        
        data: List[_FTWTestSchema] = []
        
        # find filename which match the rule id
        for root, _, files in os.walk(file_path):
            for file_name in files:
                data += self.parse_go_ftw_yaml(os.path.join(root, file_name), case_limit)

        return data
    
    def parse_go_ftw_yaml(self, file_path: str, case_limit: int = 1e10) -> List[_FTWTestSchema]:
        """_summary_
        @TODO: documentation
        Args:
            file_path (str): _description_

        Returns:
            List[_FTWTestSchema]: _description_
        """
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        res = []

        cnt = 0
        
        for data in data["tests"]:
            test_title = data['test_title']
            inputs: List[_FTWTestInput] = []
            
            for stage in data['stages']:
                inputs.append(_FTWTestInput(stage["stage"]["input"]))
                cnt += 1
                if cnt >= case_limit:
                    break
                
            test = _FTWTestSchema(test_title, inputs)
            res.append(test)
            
            if cnt >= case_limit:
                break

        return res
    
    def _get_threshold(self, file_path: str) -> List[Threshold]:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)
            return [Threshold(**data) for data in raw_data["thresholds"]]

    def _create_colored_text_by_value(self, value: any) -> str:
        color: str

        if type(value) == bool:
            color = "green" if value else "red"
        elif type(value) == float or type(value) == int:
            if value == 0:
                color = "light_grey"
            elif value > 0:
                color = "red"
                value = f"+{value}"
            else:
                color = "green"
        else:
            raise Exception("Invalid value type")

        return colored(str(value),color, attrs=["bold"])