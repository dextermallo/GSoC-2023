from .Util import ParsedDataItem, Threshold, Util
from .CollectCommandArg import CollectCommandArg
from .ReportCommandArg import ReportCommandArg
from .FTWUtil import FTWUtil
from .LocustUtil import LocustUtil
from .CAdvisorUtil import CAdvisorUtil

from src.type import UtilType

UtilMapper: dict[str, Util] = {
    UtilType.ftw.name: FTWUtil,
    UtilType.cAdvisor.name: CAdvisorUtil,
    UtilType.locust.name: LocustUtil
}


__all__ = [
    "Threshold",
    "ParsedDataItem",
    "Util",
    "CollectCommandArg",
    "ReportCommandArg",
    "UtilMapper"
]