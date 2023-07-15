from enum import Enum
from typing import List
import os
import re

class UtilType(Enum):
    ftw = "ftw",
    locust = "locust",
    cAdvisor = "cAdvisor",
    eBFF = "eBFF",
    
class State(Enum):
    before = "before"
    after = "after"

class CollectCommandArg:
    test_name: str
    utils: List[UtilType]
    before: str
    after: str
    raw_output: str
    output: str
    waf_endpoint: str
    
    # static
    # - tmp
    #    | - before-rules
    #    | - after-rules
    #    | - test-cases
    tmp_dir: str = './tmp'
    before_rules_dir: str
    after_rules_dir: str
    test_cases_dir: str
    
    # @TODO: move to config
    modsec_version: str = 'modsec2-apache'
    
    def __init__(self,
                 test_name: str,
                 utils: List[UtilType],
                 before: str,
                 after: str,
                 raw_output: str,
                 output: str,
                 waf_endpoint: str
                 ):
        self.test_name = test_name
        self.utils = utils
        self.before = before if before else "HEAD"
        self.after = after if after else "."
        
        if not isGitCommitHash(self.before) and not isGitCommitHash(self.after):
            raise Exception("Invalid before/after: only one local folder is allowed")

        if not isGitCommitHash(self.after):
            self.after = f"-- {self.after}"

        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.waf_endpoint = waf_endpoint if waf_endpoint else "http://localhost:80"
        
        self.tmp_dir = os.path.join(self.tmp_dir, self.test_name)
        self.before_rules_dir = os.path.join(self.tmp_dir, "before-rules")
        self.after_rules_dir = os.path.join(self.tmp_dir, "after-rules")
        self.test_cases_dir = os.path.join(self.tmp_dir, "test-cases")

class ReportFormat(Enum):
    text = "text",
    img = "img"

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

class ChangedRule:
    # @TODO: implement id
    id: str
    req: str

    def __init__(self, req: str):
        self.id = None
        self.req = req

def isGitCommitHash(s: str) -> bool:
    finder = re.compile(r'[0-9a-f]+')
    return s == "HEAD" or (len(s) <= 40 and finder.fullmatch(s))