#!/usr/bin/env python3

import argparse
from ast import arg
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
    oracles = benchmark.bic_location[project][case]
    ora_path = os.path.join(OUTPUT_DIR, project, case)
    with open(os.path.join(ora_path, "oracles.txt"), 'w') as of:
        of.writelines(
            map(lambda bic_loc: bic_loc[0] + ":" + str(bic_loc[1]) + '\n',
                oracles))
    cmd = [
        BLAZER_BIN, '-timestamp', timestamp, '-engine', args.engine,
        '-default_rule_prob', args.default_rule_prob, '-default_rule_prob2',
        args.default_rule_prob2, '-default_edb_prob', args.default_edb_prob,
        '-default_obsold_prob', args.default_obsold_prob,
        '-default_nc_obsold_prob', args.default_nc_obsold_prob, '-eps',
        args.eps, '-parent_dir',
        os.path.join(OUTPUT_DIR, project, case, 'parent', 'sparrow-out'),
        os.path.join(OUTPUT_DIR, project, case, 'bic', 'sparrow-out')
    ]
    if args.debug:
        cmd.append("-debug")
    if args.soft_disj:
        cmd.append("-soft_disj")
    if args.prune_cons:
        cmd.append("-prune_cons")
    if args.faulty_func:
        cmd.append("-faulty_func")
    if args.inter_sim:
        cmd.append("-inter_sim")
        cmd += ['-min_iters', args.min_iters, '-max_iters', args.max_iters]
    logging.info("Cmd: {}".format(" ".join(cmd)))
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL)


def run(args, timestamp):
    timestamp = datetime.datetime.now().strftime(
        '%Y%m%d-%H:%M:%S') if timestamp is None else timestamp
    print(timestamp)
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
    parser.add_argument('-e',
                        '--engine',
                        type=str,
                        choices=[
                            'none', 'tarantula', 'ochiai', 'jaccard',
                            'prophet', 'unival', 'dstar', 'all'
                        ],
                        default='tarantula')
    parser.add_argument('-g', '--debug', action='store_true', default=False)
    parser.add_argument('-f',
                        '--faulty_func',
                        action='store_true',
                        default=False)
    parser.add_argument('-s',
                        '--soft_disj',
                        action='store_true',
                        default=False)
    parser.add_argument('-i',
                        '--inter_sim',
                        action='store_true',
                        default=False)
    parser.add_argument('--min_iters', type=str, default="500")
    parser.add_argument('--max_iters', type=str, default="1000")
    parser.add_argument('--default_rule_prob', type=str, default="0.99")
    parser.add_argument('--default_rule_prob2', type=str, default="0.55")
    parser.add_argument('--default_edb_prob', type=str, default="0.99")
    parser.add_argument('--default_obsold_prob', type=str, default="0.01")
    parser.add_argument('--default_nc_obsold_prob', type=str, default="0.5")
    parser.add_argument('--eps', type=str, default="0.1")
    parser.add_argument('--prune_cons', action='store_true')
    parser.add_argument('--timestamp', type=str)
    args = parser.parse_args()
    run(args, args.timestamp)


if __name__ == '__main__':
    main()
