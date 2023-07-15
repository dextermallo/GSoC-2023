import yaml
import os
import json
from abc import ABC, abstractmethod
from typing import Type, List
from src.utils.logger import logger
from src.interface.FTWTestSchema import FTWTestSchema, FTWTestInput


class IUtil(ABC):
    """_summary_
    IDataCollector is an interface for data collector,
    tt is used to read data from a source and store it in a database.
    extend this class to implement your own data collector.
    
    Generally, a collector perform the following steps in linear order:
    read_data() -> save_raw_data() -> parse_data()
    
    Noted that read_data() and save_raw_data() are optional if the raw data sources
    are provided. In this case, the data can be parsed directly.
    """

    @abstractmethod
    def collect(self):
        """_summary_
        read_data() is a method for reading data from a source.
        It is an optional func to be implemented if the data source 
        (e.g., raw datafile like logs) is already provided.
        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError
    
    @abstractmethod
    def summary(self):
        """_summary_
        save_raw_data() is a method for saving raw data to a file.
        It follows the func read_data() and is used to save the data, and it 
        is an optional func to be implemented if the data source is already provided.

        Raises:
            NotImplementedError: the method is not implemented
        """
        raise NotImplementedError
    
    def _save_json_file(self, dist_path: str, data: any, cls: Type[json.JSONEncoder] = None):
        """_summary_

        Args:
            dist_path (str): _description_
            data (any): _description_
            cls (Type[json.JSONEncoder], optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        
        
        logger.debug('start: __save_json_file()')

        try:
            # create directory if not exist
            os.makedirs(os.path.dirname(dist_path), exist_ok=True)
            with open(dist_path, "w+") as file:
                json.dump(data, file, indent=2, cls=cls)
            file.close()
        except Exception as e:
            logger.error(e)
            return False

    def _save_file(self, dist_path: str, data: str):
        """_summary_

        Args:
            dist_path (str): _description_
            data (str): _description_

        Returns:
            _type_: _description_
        """
        logger.debug('start: _save_file()')

        try:
            os.makedirs(os.path.dirname(dist_path), exist_ok=True)
            with open(dist_path, "w+") as file:
                file.write(data)
            file.close()
        except Exception as e:
            logger.error(e)
            return False

    def _create_directory(self, dist_path: str):
        """_summary_
        @TODO: documentation
        Args:
            dist_path (str): _description_
        """
        os.makedirs(os.path.dirname(dist_path), exist_ok=True)
       
    def _retrieve_rule_test_file_by_id(self, file_path: str, rule_id: str) -> List[FTWTestSchema]:
        """_summary_
        @TODO: documentation
        Args:
            rule_id (str): _description_

        Raises:
            Exception: _description_

        Returns:
            List[FTWTestSchema]: _description_
        """
        logger.debug('start: _retrieve_rule_test_file_by_id()')

        if file_path is None:
            raise Exception("file_path is None")
        
        matched = []
        
        # find filename which match the rule id
        for root, _, files in os.walk(file_path):
            for file_name in files:
                if rule_id in file_name:
                    matched.append(os.path.join(root, file_name))

        data: List[FTWTestSchema] = []

        for i in matched:
            data += self.parse_go_ftw_yaml(i)

        return data
    
    def _parse_ftw_test_file(self, file_path: str, case_limit: int) -> List[FTWTestSchema]:
        logger.debug('start: _retrieve_rule_test_file_by_id()')

        if file_path is None:
            raise Exception("file_path is None")
        
        data: List[FTWTestSchema] = []
        
        # find filename which match the rule id
        for root, _, files in os.walk(file_path):
            for file_name in files:
                data += self.parse_go_ftw_yaml(os.path.join(root, file_name), case_limit)

        return data
    
    def parse_go_ftw_yaml(self, file_path: str, case_limit: int = 1e10) -> List[FTWTestSchema]:
        """_summary_
        @TODO: documentation
        Args:
            file_path (str): _description_

        Returns:
            List[FTWTestSchema]: _description_
        """
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)

        res = []

        cnt = 0
        
        for data in data["tests"]:
            test_title = data['test_title']
            inputs: List[FTWTestInput] = []
            
            for stage in data['stages']:
                inputs.append(FTWTestInput(stage["stage"]["input"]))
                cnt += 1
                if cnt >= case_limit:
                    break
                
            test = FTWTestSchema(test_title, inputs)
            res.append(test)
            
            if cnt >= case_limit:
                break

        return res