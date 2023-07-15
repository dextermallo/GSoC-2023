from enum import Enum
from typing import List

class ComparisonUnit(Enum):
    total = 1,
    each = 2,
    average = 3,
    sum = 4
    
class ComparisonMethod(Enum):
    eq = 1,
    ne = 2,
    gt = 3,
    lt = 4,
    ge = 5,
    le = 6,
    rateIsGt = 7
    rateIsLt = 8

class ParsedDataItem:
    key: any
    value: any
    labels: set
    def __init__(self, key: any, value: any, labels: List[str]):
        self.key = key
        self.value = value
        self.labels = set(labels)

class Threshold:
    id: int
    metric_name: str
    metric_desc: str
    comparison_unit: ComparisonUnit
    comparison_method: ComparisonMethod
    data_name: str

    threshold: float
    before_data_value: list
    after_data_value: list
    include_labels: List[str]
    exclude_labels: List[str]

    def __init__(self,
                 id: int,
                 metric_name: str,
                 metric_desc: str,
                 comparison_unit: ComparisonUnit,
                 comparison_method: ComparisonMethod,
                 data_name: str,
                 threshold: float,
                 include_labels: List[str],
                 exclude_labels: List[str]
                 ):
        self.id = id
        self.metric_name = metric_name
        self.metric_desc = metric_desc
        self.comparison_unit = comparison_unit
        self.comparison_method = comparison_method
        self.data_name = data_name
        self.threshold = threshold
        self.include_labels = include_labels if include_labels else None
        self.exclude_labels = exclude_labels if exclude_labels else None

    def passInspection():
        return True