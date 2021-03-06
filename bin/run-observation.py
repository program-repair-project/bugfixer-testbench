#!/usr/bin/env python3

import argparse
from asyncio.subprocess import DEVNULL
import subprocess
import os
import logging
from benchmark import benchmark, faulty_function
from pathlib import Path
import yaml

PROJECT_HOME = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_HOME / 'output'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def get_test_num(bugzoo, program, bug_id):
    for item in bugzoo:
        if item['name'] == 'manybugs:{}:{}'.format(program, bug_id):
            # print(item)
            return item['test-harness']['passing'], item['test-harness'][
                'failing']
    return 0, 0


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
            engine_list = [
                "prophet", "ochiai", "jaccard", "tarantula", "dstar"
            ]
        else:
            engine_list.append(engine)
        for e in engine_list:
            COV_PATH = OUTPUT_DIR / project / case / 'bic' / 'sparrow-out' / f'coverage_{e}.txt'
            if not COV_PATH.exists():
                logging.info(
                    "There is no coverage file. Start extracting it first")
                if e == "dstar":
                    for e_tmp in ["prophet", "ochiai", "jaccard", "tarantula"]:
                        COV_PATH_TMP = (OUTPUT_DIR / project / case / 'bic' /
                                        'sparrow-out' /
                                        f'coverage_{e_tmp}.txt')
                        if COV_PATH_TMP.exists():
                            f_cov_tmp = open(COV_PATH_TMP, 'r')
                            f_cov = open(COV_PATH, 'w')
                            YML_PATH = PROJECT_HOME / 'benchmark' / project / f'{project}.bugzoo.yml'
                            f_yml = open(YML_PATH, 'r')
                            bugzoo = yaml.load(f_yml, Loader=yaml.FullLoader)
                            p_num, f_num = get_test_num(
                                bugzoo['bugs'], project, case)
                            cov_tmp_lines = f_cov_tmp.readlines()
                            result = []
                            max = 0
                            min = float('inf')
                            for line in cov_tmp_lines:
                                filename, linenum, pt, ft, _ = line.replace(
                                    ':', ',').split(',')
                                if ((int(f_num) - int(ft)) + int(pt)) != 0:
                                    score = (int(ft)**2) / (
                                        (int(f_num) - int(ft)) + int(pt))
                                    if score > max:
                                        max = score
                                    if score < min:
                                        min = score
                                else:
                                    score = -1
                                result.append(
                                    (filename, linenum, pt, ft, score))
                            result = list(
                                map(
                                    lambda x: (x[0], x[1], x[2], x[3], (
                                        (x[4] - min) / (max - min)) * 0.9
                                               if x[4] != -1 else 1.0), result))
                            result.sort(key=lambda x: x[4], reverse=True)
                            for f, l, pt, ft, s in result:
                                f_cov.write(f'{f}:{l},{pt},{ft},{s:.6f}\n')

                            f_cov_tmp.close()
                            f_cov.close()
                            break
                    else:
                        logging.error(
                            "There is no other coverage file for dstar.")
                        continue
                else:
                    cmd = [
                        str(PROJECT_HOME / 'bin' / 'coverage.py'), '-p',
                        project, '-c', case, '-e', engine
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
    parser.add_argument('-e',
                        '--engine',
                        type=str,
                        choices=[
                            'tarantula', 'ochiai', 'jaccard', 'dstar',
                            'prophet', 'unival', 'all'
                        ],
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
