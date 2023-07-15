import argparse
import sys
import os
from src.type import ReportCommandArg, UtilType
from src.utils.ftw import FTWUtil
from src.utils.cAdvisor import CAdvisorUtil
from src.utils.locust import LocustUtil


UtilMapper: dict = {
    UtilType.ftw.name: FTWUtil,
    UtilType.cAdvisor.name: CAdvisorUtil,
    UtilType.locust.name: LocustUtil
}

def get_summary_command_arg(*args) -> ReportCommandArg:
    parser = argparse.ArgumentParser(description='WAF Test Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils')
    parser.add_argument('--output', type=str, help='output')
    parser.add_argument('--raw-output', type=str, help='raw output')
    parser.add_argument('--threshold-conf', type=str, help='threshold conf')
    parser.add_argument('--format', type=str, help='output')
    parsed_args = parser.parse_args()
    
    # @TODO: default with all utils
    return ReportCommandArg(
        test_name=parsed_args.test_name,
        utils=parsed_args.utils.split(',') if parsed_args.utils else [],
        output=parsed_args.output,
        raw_output=parsed_args.raw_output,
        threshold_conf=parsed_args.threshold_conf,
        format=parsed_args.format
    )

def init(args: ReportCommandArg):
    # create folder for output
    os.makedirs(args.output, exist_ok=True)
        
def main():
    # check the inputs
    args = get_summary_command_arg(sys.argv)

    # create folder
    init(args)
    
    # build the report
    for util in args.utils:
        UtilMapper[util]().report(args)
