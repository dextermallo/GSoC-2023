import json


class DataFormat:
    """_summary_
    @TODO: doc
    """

    timestamp: str
    val: any
    
    def __init__(self, timestamp: str, val: any):
        self.timestamp = timestamp
        self.val = val
        

class DataFormatEncoder(json.JSONEncoder):
    """_summary_
    @TODO: doc
    """
    def default(self, obj):
        if isinstance(obj, DataFormat):
            return obj.__dict__
        return super().default(obj)