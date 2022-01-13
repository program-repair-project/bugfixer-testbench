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
    SRC_PATH = os.path.join(os.path.dirname(RESULT_PATH), 'src')
    grep = subprocess.run(['grep', '-rh', var_ver, SRC_PATH],
                          capture_output=True,
                          text=True)
    try:
        grep.check_returncode()
    except:
        logging.warning(f'Not found: {var}')
        return "No_loc:-1"
    out = []
    for output in grep.stdout.splitlines():
        if "fprintf" in output:
            out.append(output)
    if not out:
        logging.warning(f'Not found: {var_ver}')
        return "No_loc:-1"
    out = out[0].split('"')[1].split(',')
    return f'{out[0]}:{out[2]}'


def run_one(project, case):
    logging.info(f"Printing observation result: {project}-{case}")
    RESULT_PATH = os.path.join(OUT_DIR, project, case, 'unival', 'unival')
    COV_PATH = os.path.join(OUT_DIR, project, case, 'bic', 'sparrow-out',
                            'coverage_unival.txt')
    with open(os.path.join(RESULT_PATH, 'resultUniVal.csv'),
              newline='') as csvfile:
        result_unival = csv.reader(csvfile, delimiter=',')
        for line in result_unival:
            if line[0] == "":
                var_list = line[1:]
            elif line[0] == "1":
                score_list = line[1:]
    assert len(var_list) == len(score_list)
    loc_score_map = {}
    for var, score in zip(var_list, score_list):
        loc = var2loc(var, RESULT_PATH)
        score = float(score)
        if loc not in loc_score_map:
            loc_score_map[loc] = score
        elif loc_score_map[loc] < score:
            loc_score_map[loc] = score
    loc_score_assoc = sorted(loc_score_map.items(),
                             key=lambda item: item[1],
                             reverse=True)
    with open(COV_PATH, 'w') as result_file:
        for loc, score in loc_score_assoc:
            result_file.write(f'{loc},0,0,{score}\n')


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
