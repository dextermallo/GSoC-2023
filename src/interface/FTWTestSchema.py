from src.utils.logger import logger
from typing import List


class FTWTestInput:
    """_summary_
    @TODO: documentation
    """
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

class FTWTestSchema:
    """_summary_
    @TODO: documentation
    """
    test_title: str
    stages: List[FTWTestInput]
    
    def __init__(self, test_title: str, stages: List[FTWTestInput]):
        self.test_title = test_title
        self.stages = stages