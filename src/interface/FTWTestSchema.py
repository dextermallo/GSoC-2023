from typing import List


class FTWTestInput:
    """_summary_
    @TODO: documentation
    """
    method: str
    port: int
    headers: dict
    data: str
    uri: str
    
    def __init__(self, dict: dict):
        for k, v in dict.items():
            setattr(self, k, v)

class FTWTestSchema:
    """_summary_
    @TODO: documentation
    """
    test_title: str
    stages: List[FTWTestInput]
    
    def __init__(self, test_title: str, stages: List[FTWTestInput]):
        self.test_title = test_title
        self.stages = stages