import os
import json
import secrets
import string
from abc import ABC, abstractmethod
from typing import Type
from src.utils.loader import logger
from src.interface.DataFormat import DataFormat

class IDataCollector(ABC):
    """_summary_
    @TODO: doc
    IDataCollector is an interface for data collector,
    tt is used to read data from a source and store it in a database.
    extend this class to implement your own data collector.
    
    """

    @abstractmethod
    def read_data(self):
        raise NotImplementedError
    
    @abstractmethod
    def save_raw_data(self):
        raise NotImplementedError
    
    @abstractmethod
    def parse_data(self):
        raise NotImplementedError
    
    def _save_json_file(self, dist_path: str, data: any, cls: Type[json.JSONEncoder] = None):
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
        
    def _is_validate_data_format(self, data: any):
        logger.debug('start: is_validate_data_format()')
        
        # if data is list, check all items in list
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, DataFormat):
                    logger.error(f"Data is not DataFormat: {item}")
                    return False
        else:
            if not isinstance(data, DataFormat):
                logger.error("Data is not DataFormat: {data}")
                return False

        return True
    
    def _generate_group_suffix(self) -> str:
        random_string = ''.join(secrets.choice(string.digits) for _ in range(6))
        return random_string