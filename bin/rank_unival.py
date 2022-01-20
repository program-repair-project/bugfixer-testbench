#!/usr/bin/env python3

import os
import argparse
from benchmark import benchmark, bic_location
import subprocess

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(PROJECT_HOME, 'output')


def print_one_result(project, case):
    OBS_PATH = os.path.join(OUT_DIR, project, case, 'bic', 'sparrow-out',
                            'observation_unival.txt')
    search_term_list = map(lambda l: f'{l[0]}:{l[1]}',
                           bic_location[project][case])
    rank = None
    for search_term in search_term_list:
        grep = subprocess.run(['grep', '-n', search_term, OBS_PATH],
                              capture_output=True,
                              text=True)
        try:
            grep.check_returncode()
        except subprocess.CalledProcessError:
            pass
        else:
            cand = int(grep.stdout.split(':')[0])
            rank = cand if not rank or rank > cand else rank

    wc = subprocess.run(['wc', '-l', OBS_PATH], capture_output=True, text=True)
    try:
        wc.check_returncode()
    except subprocess.CalledProcessError:
        print('There is no obs result file.')
        return
    total = wc.stdout.split()[0]

    if not rank:
        print(f'{project}\t{case}\t{-1:3d}\t{total}')
    else:
        print(f'{project}\t{case}\t{rank:3d}\t{total}')


def print_result(args):
    project, case = args.project, args.case
    if project:
        if case:
            print_one_result(project, case)
        else:
            for case in benchmark[project]:
                print_one_result(project, case)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                print_one_result(project, case)


def main():
    parser = argparse.ArgumentParser(description='Print rank of UniVal result')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    args = parser.parse_args()
    print_result(args)


if __name__ == '__main__':
    main()
