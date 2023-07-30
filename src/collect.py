import docker
from ping3 import ping

import argparse
import sys
import os
import time
import subprocess
import shutil
from typing import List

from src.model import CollectCommandArg, UtilMapper
from src.type import State
from src.utils import logger


class _ChangedRule:
    # @TODO: implement id
    req: str

    def __init__(self, req: str):
        self.req = req

def get_test_command_arg(*args) -> CollectCommandArg:
    parser = argparse.ArgumentParser(description='WAF Collect Command Parser')
    parser.add_argument('--test-name', type=str, help='test name', required=True)
    parser.add_argument('--utils', type=str, help='utils')
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
        utils=None if parsed_args.utils is None else parsed_args.utils.split(","),
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

def get_changed_rules(arg: CollectCommandArg) -> List[_ChangedRule]:
    exec_cmd = f"git diff --name-only {arg.before} {arg.after} | grep -E \'rules/.*.conf$\'"
    
    subprocess.run(exec_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = subprocess.check_output(exec_cmd, shell=True).decode()
        
    changedRules: List[_ChangedRule] = []
        
    for line in output.splitlines():
        logger.info(f"Changed rule: {line}")
        changedRules.append(_ChangedRule(line.replace("rules/", "").replace(".conf", "")))

    return changedRules

def init_tmp_file(arg: CollectCommandArg, changedRules: List[_ChangedRule]):
    # copy before-rules
    for changedRule in changedRules:
        cmd = f"git show {arg.before}:rules/{changedRule.req}.conf > {arg.before_rules_dir}/{changedRule.req}.conf"
        subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
    cmd = f"""sed -i -e "s/- ..\\/rules/- ..\\/{processed_path}/g" .\\/tests\\/docker-compose-{state.name}.yml"""
    # cmd = f"""sed -i -e "s/- ..\/rules/- ..\/{processed_path}/g" .\/tests\/docker-compose-{state.name}.yml"""
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # @TODO: this is a temporary fix for extra files created from sed
    os.remove(f"./tests/docker-compose-{state.name}.yml-e")

def runner(args: CollectCommandArg, state: State):
    # start service with docker-compose
    cmd = f"docker-compose -f ./tests/docker-compose-{state.name}.yml up -d {args.modsec_version}"

    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)

    # check it's up and running
    if not waf_server_is_up(args.waf_endpoint):
        logger.critical("WAF server is not up")
        exit(1)

    # run test cases
    for util in args.utils:
        logger.info(f"Running Test case: {args.test_name} using {util}, State = {state.name}")
        UtilMapper.get(util)().collect(args, state)
    
    # stop service with docker-compose
    cmd = f"""
    docker-compose -f ./tests/docker-compose-{state.name}.yml stop &&
    docker-compose -f ./tests/docker-compose-{state.name}.yml down
    """
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, capture_output=False)

def waf_server_is_up(waf_endpoint: str) -> bool:
    timeout, retry = 5, 0
    
    # @TODO: update
    while retry < 3:
        if docker.from_env().api.inspect_container("modsec2-apache")["State"]["Status"] == 'running':
            return True
        retry += 1
        time.sleep(timeout)
    
    retry = 0

    while retry < 3:
        result = ping(waf_endpoint, timeout=timeout)
        if result is None or not result:
            retry += 1
            time.sleep(timeout)
            continue
        else:
            return True

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
    runner(args, State.before)
    
    init_docker_compose_file(args, State.after)
    runner(args, State.after)