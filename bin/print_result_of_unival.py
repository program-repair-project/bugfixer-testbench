#!/usr/bin/env python3

import argparse
import os
import subprocess
import csv
import logging
from benchmark import benchmark

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(PROJECT_HOME, 'output')

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")


def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def var2loc(var, RESULT_PATH):
    print(var)
    var_ver = rreplace(var, '_', ',', 1)
    result_file = os.path.join(RESULT_PATH, 'output.txt')
    grep = subprocess.run(['grep', '-a', f',{var_ver}', result_file],
                          capture_output=True,
                          text=True)
    try:
        grep.check_returncode()
    except:
        logging.warning("Not found:", var)
        return "No_loc:-1"
    out = grep.stdout.split('\n')[0].split(',')
    return f'{out[0]}:{out[2]}'


def run_one(project, case):
    logging.info(f"Printing observation result: {project}-{case}")
    RESULT_PATH = os.path.join(OUT_DIR, project, case, 'unival', 'unival')
    with open(os.path.join(RESULT_PATH, 'resultUniVal.csv'),
              newline='') as csvfile:
        result_unival = csv.reader(csvfile, delimiter=',')
        for line in result_unival:
            if line[0] == "":
                var_list = line[1:]
            elif line[0] == "1":
                score_list = line[1:]
    assert len(var_list) == len(score_list)
    with open(os.path.join(RESULT_PATH, 'observation.txt'),
              'w') as result_file:
        for var, score in zip(var_list, score_list):
            result_file.write(f'{var2loc(var, RESULT_PATH)},0,0,{score}\n')


def run(args):
    project, case = args.project, args.case
    if project:
        if case:
            run_one(project, case)
        else:
            for case in benchmark[project]:
                run_one(project, case)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                run_one(project, case)


def main():
    parser = argparse.ArgumentParser(description='Print result of unival')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    args = parser.parse_args()
    if not os.path.isdir(OUT_DIR):
        raise Exception("There is no output directory. Run Unival first.")
    run(args)


if __name__ == '__main__':
    main()