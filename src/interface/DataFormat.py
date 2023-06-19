import json
from typing import List


class DataFormat:
    """_summary_
    @TODO: doc
    """

    x_axis_metadata: str
    y_axis_metadata: str
    x_data: List[any]
    y_data: List[any]
    
    def __init__(self, x_axis_metadata: str, y_axis_metadata: str):
        self.x_axis_metadata = x_axis_metadata
        self.y_axis_metadata = y_axis_metadata
        self.x_data = []
        self.y_data = []
        
    def append(self, x_data: any, y_data: any):
        self.x_data.append(x_data)
        self.y_data.append(y_data)
        

class DataFormatEncoder(json.JSONEncoder):
    """_summary_
    @TODO: doc
    """
    def default(self, obj):
        if isinstance(obj, DataFormat):
            return obj.__dict__
        return super().default(obj)