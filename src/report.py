import argparse
import sys
import os
from src.type import ReportCommandArg, ReportFormat
from src.utils import UtilMapper, logger


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
        if args.format == ReportFormat.text:
            UtilMapper[util]().text_report(args)

        elif args.format == ReportFormat.img:
            UtilMapper[util]().figure_report(args)

        else:
            logger.critical("--format support text or img")
            exit(1)