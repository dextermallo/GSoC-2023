import argparse
import sys
import os
import time
from typing import List
from src.utils.logger import logger
import subprocess
import shutil
from src.type import CollectCommandArg, State, ChangedRule, UtilType
from src.utils.ftw import FTWUtil
from src.utils.cAdvisor import CAdvisorUtil
from src.utils.locust import LocustUtil
from src.utils.utils import container_is_healthy


UtilMapper: dict = {
    UtilType.ftw.name: FTWUtil,
    UtilType.cAdvisor.name: CAdvisorUtil,
    UtilType.locust.name: LocustUtil
}

def get_test_command_arg(*args) -> CollectCommandArg:
    parser = argparse.ArgumentParser(description='WAF Test Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils', required=True)
    parser.add_argument('--before', type=str, help='before test command')
    parser.add_argument('--after', type=str, help='after test command')
    parser.add_argument('--raw-output', type=str, help='raw output')
    parser.add_argument('--output', type=str, help='output')
    parser.add_argument('--waf-endpoint', type=str, help='waf endpoint')
    
    parsed_args = parser.parse_args()
    
    return CollectCommandArg(
        test_name=parsed_args.test_name,
        before=parsed_args.before,
        after=parsed_args.after,
        utils=parsed_args.utils.split(","),
        raw_output=parsed_args.raw_output,
        output=parsed_args.output,
        waf_endpoint=parsed_args.waf_endpoint
    )

def init(arg: CollectCommandArg):
    # create folder for raw_output
    os.makedirs(arg.raw_output, exist_ok=True)
    
    # create folder for output
    os.makedirs(arg.output, exist_ok=True)
    
    # create folder for tmp
    os.makedirs(arg.tmp_dir, exist_ok=True)
    
    # create folder for test case
    os.makedirs(arg.raw_output, exist_ok=True)
    os.makedirs(arg.output, exist_ok=True)
    os.makedirs(arg.tmp_dir, exist_ok=True)
    os.makedirs(arg.before_rules_dir, exist_ok=True)
    os.makedirs(arg.after_rules_dir, exist_ok=True)
    os.makedirs(arg.test_cases_dir, exist_ok=True)

def get_changed_rules(arg: CollectCommandArg) -> List[ChangedRule]:
    exec_cmd = f"git diff --name-only {arg.before} {arg.after} | grep -E \'rules/.*.conf\'"
    
    subprocess.run(exec_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = subprocess.check_output(exec_cmd, shell=True).decode()
        
    changedRules: List[ChangedRule] = []
        
    for line in output.splitlines():
        logger.info(f"Changed rule: {line}")
        changedRules.append(ChangedRule(line.replace("rules/", "").replace(".conf", "")))

    return changedRules

def init_tmp_file(arg: CollectCommandArg, changedRules: List[ChangedRule]):
    # copy before-rules
    for changedRule in changedRules:
        cmd = f"git show {arg.before}:rules/{changedRule.req}.conf > {arg.before_rules_dir}/{changedRule.req}.conf"
        
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = subprocess.check_output(cmd, shell=True).decode()
    
    # copy after-rules
    for changedRule in changedRules:
        cmd: str
        
        if arg.after.startswith("--"):
            cmd = f"cp {arg.after}/rules/{changedRule.req}.conf {arg.after_rules_dir}/{changedRule.req}.conf"
        else:
            cmd = f"git show {arg.after}:rules/{changedRule.req}.conf > {arg.after_rules_dir}/{changedRule.req}.conf"
        
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = subprocess.check_output(cmd, shell=True).decode()
    
    # copy regression files for changedRules to tmp folder
    for changedRule in changedRules:
        try:
            shutil.copytree(f"./tests/regression/tests/{changedRule.req}/", f"{arg.test_cases_dir}/{changedRule.req}/")
        except OSError as e:
            logger.warning(f"Test case for {changedRule.req} does not have test case")

def init_docker_compose_file(arg: CollectCommandArg, state: State):
    shutil.copyfile("./tests/docker-compose.yml", f"./tests/docker-compose-{state.name}.yml")
    processed_path = (arg.before_rules_dir if state == State.before else arg.after_rules_dir).replace("/", "\\/")    
    cmd = f"""sed -i -e "s/- ..\/rules/- ..\/{processed_path}/g" .\/tests\/docker-compose-{state.name}.yml"""
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _ = subprocess.check_output(cmd, shell=True).decode()

def runner(args: CollectCommandArg, changedRules: List[ChangedRule], state: State):
    # start service with docker-compose
    cmd = f"docker-compose -f ./tests/docker-compose-{state.name}.yml up -d {args.modsec_version}"
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _ = subprocess.check_output(cmd, shell=True).decode()

    # check it's up and running
    if not waf_server_is_up(args.waf_endpoint):
        raise Exception("WAF server is not up")

    # run test cases
    for util in args.utils:
        logger.warning(f"Running {util}...")
        UtilMapper.get(util)(args, state).collect()
    
    # stop service with docker-compose
    cmd = f"""
    docker-compose -f ./tests/docker-compose-{state.name}.yml stop &&
    docker-compose -f ./tests/docker-compose-{state.name}.yml down
    """
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _ = subprocess.check_output(cmd, shell=True).decode()

def waf_server_is_up(was_endpoint: str) -> bool:
    timeout, retry = 10, 0
    
    # @TODO: update
    while retry < 3:
        if container_is_healthy("modsec2-apache"):
            return True
        retry += 1
        time.sleep(timeout)
    return False

def cleanup():
    # remove if necessary
    pass
    
def main():
    # check the inputs
    args = get_test_command_arg(sys.argv)

    # create folder
    init(args)
    
    # get corresponding test files
    changedRules = get_changed_rules(args)
    
    # if there's no changed rule, exit
    if len(changedRules) == 0:
        logger.info("No rule is changed")
        exit(0)
    
    # init temp file for testing    
    init_tmp_file(args, changedRules)
    
    init_docker_compose_file(args, State.before)
    runner(args, changedRules, State.before)
    
    init_docker_compose_file(args, State.after)
    runner(args, changedRules, State.after)
