import re
import os
from typing import List, Optional

from src.type import UtilType


class CollectCommandArg:
    """@TODO: doc"""
    test_name: str
    utils: List[UtilType]
    before: Optional[str]
    after: Optional[str]
    raw_output: Optional[str]
    output: Optional[str]
    waf_endpoint: Optional[str]

    # Auto generated
    tmp_dir: str = './tmp'
    before_rules_dir: str
    after_rules_dir: str
    test_cases_dir: str
    
    # @TODO: move to config
    modsec_version: str = 'modsec2-apache'
    
    def __init__(self,
                 test_name: str,
                 utils: Optional[List[UtilType]],
                 raw_output: Optional[str],
                 output: Optional[str],
                 before: Optional[str],
                 after: Optional[str],
                 waf_endpoint: Optional[str]
                 ):
        self.test_name = test_name
        self.utils = utils if (utils is not None and len(utils)) else [util for util in UtilType]
        self.before = before if before else "HEAD"
        self.after = after if after else "."
        
        if not self.__isGitCommitHash(self.before) and not self.__isGitCommitHash(self.after):
            raise Exception("Invalid before/after: only one local folder is allowed")

        if not self.__isGitCommitHash(self.after):
            self.after = f"-- {self.after}"

        self.raw_output = f"{raw_output}/{self.test_name}" if raw_output else f"./data/{self.test_name}"
        self.output = f"{output}/{self.test_name}" if output else f"./report/{self.test_name}"
        self.waf_endpoint = waf_endpoint if waf_endpoint else "http://localhost:80"
        
        self.tmp_dir = os.path.join(self.tmp_dir, self.test_name)
        self.before_rules_dir = os.path.join(self.tmp_dir, "before-rules")
        self.after_rules_dir = os.path.join(self.tmp_dir, "after-rules")
        self.test_cases_dir = os.path.join(self.tmp_dir, "test-cases")
 
    def __isGitCommitHash(self, s: str) -> bool:
        finder = re.compile(r'[0-9a-f]+')
        return s == "HEAD" or (len(s) <= 40 and finder.fullmatch(s))