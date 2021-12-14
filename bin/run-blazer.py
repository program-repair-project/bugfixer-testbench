#!/usr/bin/env python3

import argparse
import datetime
import time
import logging
import os
import subprocess
import sys
import benchmark

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_HOME, "output")
BINGO_DIR = os.path.join(PROJECT_HOME, "bingo")
BLAZER_BIN = os.path.join(BINGO_DIR, "bin", "blazer")

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S",
                    filemode = 'w',
                    filename=os.path.join(PROJECT_HOME, 'run-blazer.log'))


def run_blazer(args, timestamp, project, case):
    cmd = [
        BLAZER_BIN, '-timestamp', timestamp, '-default_edb_prob',
        args.default_edb_prob, '-parent_dir',
        os.path.join(OUTPUT_DIR, project, case, 'parent', 'sparrow-out'),
        os.path.join(OUTPUT_DIR, project, case, 'bic', 'sparrow-out')
    ]
    if args.debug:
        cmd.append("-debug")
    logging.info("Cmd: {}".format(" ".join(cmd)))
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)


def run(args):
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S')
    print("Timestamp: " + timestamp)
    logging.info("Timestamp: " + timestamp)
    child_processes = []
    if args.project == "all":
        for project in benchmark.benchmark:
            for case in benchmark.benchmark[project]:
                child_processes.append(
                    run_blazer(args, timestamp, project, case))
    elif args.project in benchmark.benchmark and args.case == None:
        for case in benchmark.benchmark[args.project]:
            child_processes.append(
                run_blazer(args, timestamp, args.project, case))
    elif args.project in benchmark.benchmark and args.case in benchmark.benchmark[
            args.project]:
        child_processes.append(
            run_blazer(args, timestamp, args.project, args.case))
    else:
        print('Unknown project or case')
        exit(1)

    for cp in child_processes:
        cp.wait()


def main():
    parser = argparse.ArgumentParser(description='Run Blazer')
    parser.add_argument('-p', '--project', type=str, default="all")
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('-g', '--debug', action='store_true', default=False)
    parser.add_argument('--default_edb_prob', type=str, default="0.5")
    args = parser.parse_args()
    run(args)


if __name__ == '__main__':
    main()
