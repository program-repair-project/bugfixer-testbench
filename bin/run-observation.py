#!/usr/bin/env python3

import argparse
from asyncio.subprocess import DEVNULL
import subprocess
import os
import logging
from benchmark import benchmark, faulty_function
from pathlib import Path

PROJECT_HOME = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_HOME / 'output'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def run_one_observe(args, project, case, engine, is_faulty_func=False):
    def run_cmd_and_check(cmd,
                          *,
                          capture_output=False,
                          text=False,
                          stdout=None,
                          stderr=None):
        process = subprocess.run(cmd,
                                 capture_output=capture_output,
                                 text=text,
                                 stdout=stdout,
                                 stderr=stderr)
        try:
            process.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}-{case} failure: {" ".join(cmd)}')
        return process

    # run unival_backend if engine is unival
    if engine == 'unival':
        UNIVAL_RESULT_PATH = OUTPUT_DIR / project / case / 'unival'
        if not UNIVAL_RESULT_PATH.exists():
            logging.info("Start running UniVal frontend first")
            cmd = [
                str(PROJECT_HOME / 'bin' / 'coverage.py'), '-p', project, '-c',
                case, '-e', engine
            ]
            cmd = cmd + ['-f'] if is_faulty_func else cmd
            run_cmd_and_check(cmd)

        if (UNIVAL_RESULT_PATH / 'unival').exists():
            logging.info("UniVal is already executed. Skip")
            return
        logging.info("Start running UniVal backend")
        run_cmd_and_check([
            str(PROJECT_HOME / 'bin' / 'unival_backend.py'), '-p', project,
            '-c', case
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
        run_cmd_and_check([
            str(PROJECT_HOME / 'bin' / 'print_result_of_unival.py'), '-p',
            project, '-c', case
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    else:
        engine_list = []
        if engine == 'all':
            engine_list = ["prophet", "ochiai", "jaccard", "tarantula"]
        else:
            engine_list.append(engine)
        for e in engine_list:
            COV_PATH = OUTPUT_DIR / project / case / 'bic' / 'sparrow-out' / f'coverage_{e}.txt'
            if not COV_PATH.exists():
                logging.info(
                    "There is no coverage file. Start extracting it first")
                cmd = [
                    str(PROJECT_HOME / 'bin' / 'coverage.py'), '-p', project,
                    '-c', case, '-e', engine
                ]
                cmd = cmd + (['-g'] if args.gcov else [])
                run_cmd_and_check(cmd)

            OBS_PATH = COV_PATH.parent / f'observation_{e}.txt'
            run_cmd_and_check(
                ['cp', str(COV_PATH), str(OBS_PATH)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
            run_cmd_and_check(['sed', '-i', 's/,.*,.*,/,/g',
                               str(OBS_PATH)],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)


def run_observe(args):
    project, case, engine, is_faulty_func = args.project, args.case, args.engine, args.faulty_func

    if project:
        if case:
            run_one_observe(args, project, case, engine, is_faulty_func)
        else:
            for case in benchmark[project]:
                run_one_observe(args, project, case, engine, is_faulty_func)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                run_one_observe(args, project, case, engine, is_faulty_func)


def main():
    parser = argparse.ArgumentParser(
        description='Get observation data of project-case')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument(
        '-e',
        '--engine',
        type=str,
        choices=['tarantula', 'ochiai', 'jaccard', 'prophet', 'unival', 'all'],
        default='tarantula')
    parser.add_argument('-f',
                        '--faulty_func',
                        action='store_true',
                        default=False)
    parser.add_argument('-g', '--gcov', action='store_true', default=False)
    args = parser.parse_args()
    run_observe(args)


if __name__ == '__main__':
    main()
