from typing import List


class ParsedDataItem:
    key: any
    value: any
    labels: set
    def __init__(self, key: any, value: any, labels: List[str] = []):
        self.key = key
        self.value = value
        self.labels = set(labels)