from enum import Enum
from typing import List
from src.utils.logger import logger
from src.utils.utils import color_text


class ComparisonUnit(Enum):
    each = 1,
    average = 2,
    sum = 3,
    cnt = 4

class ComparisonMethod(Enum):
    eq = 1,
    ne = 2,
    gt = 3,
    lt = 4,
    ge = 5,
    le = 6,

    # @TODO: currently, rate_fn only supports to compare with object before
    ratioIsGt = 7
    ratioIsLt = 8
    ratioIsGe = 9
    ratioIsLe = 10

data_processing_fn = {
    ComparisonMethod.eq.name: lambda a, b: a == b,
    ComparisonMethod.ne.name: lambda a, b: a != b,
    ComparisonMethod.ge.name: lambda a, b: a > b,
    ComparisonMethod.lt.name: lambda a, b: a < b,
    ComparisonMethod.ge.name: lambda a, b: a >= b,
    ComparisonMethod.le.name: lambda a, b: a <= b,
    ComparisonMethod.ratioIsGt.name: lambda a, b: a > b,
    ComparisonMethod.ratioIsLt.name: lambda a, b: a < b,
    ComparisonMethod.ratioIsGe.name: lambda a, b: a >= b,
    ComparisonMethod.ratioIsLe.name: lambda a, b: a <= b,
}

class ComparisonObject(Enum):
    threshold = 1,
    before = 2,

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
    threshold_name: str
    threshold_desc: str
    comparison_unit: ComparisonUnit
    comparison_method: ComparisonMethod
    comparison_object: ComparisonObject
    metric_name: str

    threshold: float
    
    # if include_labels is None, then include all labels
    # if include_labels not None, then the threshold inspection only applies to
    # the data with the labels in include_labels, it is a OR condition
    include_labels: set
    exclude_labels: set

    def __init__(self,
                 id: int,
                 threshold_name: str,
                 threshold_desc: str,
                 comparison_unit: ComparisonUnit,
                 comparison_method: ComparisonMethod,
                 comparison_object: ComparisonObject,
                 metric_name: str,
                 threshold: float,
                 include_labels: List[str],
                 exclude_labels: List[str]
                 ):
        self.id = id
        self.threshold_name = threshold_name
        self.threshold_desc = threshold_desc
        self.comparison_unit = comparison_unit
        self.comparison_method = comparison_method
        self.comparison_object = comparison_object
        self.metric_name = metric_name
        self.threshold = threshold
        self.include_labels = set(include_labels) if include_labels else None
        self.exclude_labels = set(exclude_labels) if exclude_labels else None

    def isPassed(self, before_data: List[ParsedDataItem], after_data: List[ParsedDataItem]) -> bool:
        if before_data is None or after_data is None:
            logger.error("before_data or after_data is None")
            return False
        
        if len(before_data) == 0 or len(after_data) == 0:
            logger.error("before_data or after_data is empty")
            return False

        before_val_type, after_val_type = type(before_data[0].value), type(after_data[0].value)

        if before_val_type != after_val_type:
            logger.error("before_data and after_data have different type")
            return False
        
        if (before_val_type in [str, bool]) and self.comparison_method not in ['eq', 'ne']:
            logger.error(f"str/bool type only support comparison method: eq, ne")
            return False

        if not (before_val_type in [str, int, float, bool]):
            logger.error("current support data type: int, float, bool, str")
            return False
        
        if self.comparison_method in [7, 8, 9, 10] and self.comparison_object == ComparisonObject.threshold:
            logger.error("rate comparison method only support with object: before")
            return False
        
        # filter data
        before_data = [data for data in before_data if self.__filter_by_labels(data)]
        after_data = [data for data in after_data if self.__filter_by_labels(data)]
        
        # process value by comparison_unit
        if self.comparison_unit == ComparisonUnit.cnt.name:
            before_data = [ParsedDataItem("cnt", len(before_data), [])]
            after_data = [ParsedDataItem("cnt", len(after_data), [])]
        elif self.comparison_unit == ComparisonUnit.sum.name:
            before_data = [ParsedDataItem("sum", sum([data.value for data in before_data]), [])]
            after_data = [ParsedDataItem("sum", sum([data.value for data in after_data]), [])]
        elif self.comparison_unit == ComparisonUnit.average.name:
            before_data = [ParsedDataItem("average", sum([data.value for data in before_data]) / len(before_data), [])]
            after_data = [ParsedDataItem("average", sum([data.value for data in after_data]) / len(after_data), [])]
        elif self.comparison_unit == ComparisonUnit.each.name:
            pass
        
        # evaluate the value
        # @TODO: current only support same-length data
        # impl a non-length-sensitive version (e.g., time)
        if self.comparison_unit == ComparisonUnit.each and len(before_data) != len(after_data):
            raise Exception("before_data and after_data have different length")

        passed, res = False, True
        for idx in range(len(after_data)):
            # @TODO: optimize enum issue
            if self.comparison_method in [ComparisonMethod.ratioIsGt.name, ComparisonMethod.ratioIsLt.name, ComparisonMethod.ratioIsGe.name, ComparisonMethod.ratioIsLe.name]:
                ratio = after_data[idx].value / before_data[idx].value
                passed = data_processing_fn[self.comparison_method](self.threshold, ratio)
            else:
                passed = data_processing_fn[self.comparison_method](before_data[idx].value, after_data[idx].value)
            
            if not passed:
                print(color_text((
                    f"\nThreshold {self.id} failed: \n"
                    f"threshold_name: {self.threshold_name}\n"
                    f"threshold_desc: {self.threshold_desc}\n"
                    f"        before: {before_data[idx].value}\n"
                    f"         after: {after_data[idx].value}\n\n"
                ), 'red', True))
                res = False

        return res
    
    def __filter_by_labels(self, data: ParsedDataItem) -> bool:
        # check include
        res = True

        if (self.include_labels is not None) and (len(self.include_labels) > 0):
            for label in data.labels:
                if label in self.include_labels:
                    res = True
        
        if not res: 
            return False
        
        # check exclude
        if (self.exclude_labels is not None) and (len(self.exclude_labels) > 0):
            for label in data.labels:
                if label in self.exclude_labels:
                    res = False
        
        return res
