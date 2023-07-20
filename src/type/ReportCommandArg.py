from typing import List
from .UtilType import UtilType
from .ReportFormat import ReportFormat
    

class ReportCommandArg:
    test_name: str
    utils: List[UtilType]
    output: str
    raw_output: str
    threshold_conf: str
    format: ReportFormat
    
    def __init__(self,
                 test_name: str,
                 utils: List[UtilType],
                 output: str,
                 raw_output: str,
                 threshold_conf: str,
                 format: ReportFormat
                 ):
        self.test_name = test_name
        self.utils = utils
        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.threshold_conf = threshold_conf if threshold_conf else None
        self.format = format if format else ReportFormat.text