#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import os
import subprocess
import sys
import yaml
import json

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOCALIZER_HOME = os.path.join(PROJECT_HOME, "bug-localizer")
LOCALIZER_BIN_DIR = os.path.join(LOCALIZER_HOME, "_build/default/src")
SYNTHESIZER_HOME = os.path.join(PROJECT_HOME, "patch-synthesizer")
SYNTHESIZER_BIN_DIR = os.path.join(SYNTHESIZER_HOME, "_build/default/src")
MANYBUGS_HOME = os.path.join(PROJECT_HOME, "ManyBugs")

DOCKER_IN_DIR = '/bugfixer'

logging.basicConfig(level=logging.INFO, \
                    format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s", \
                    datefmt="%H:%M:%S")

timestamp = datetime.today().strftime('%Y%m%d-%H:%M:%S')
out_dir = os.path.join('bugfixer-out', timestamp)
bug_desc_file = os.path.join(PROJECT_HOME, out_dir, 'bug_desc.json')


def initialize():
    os.makedirs(out_dir)


def find_bug_desc(bugzoo, program, bug_id):
    for item in bugzoo:
        print(item)
        if item['name'] == 'manybugs:{}:{}'.format(program, bug_id):
            return item

    return None


def preprocess_bug_desc(program, bug_id):
    yml = os.path.join(MANYBUGS_HOME, program, program + '.bugzoo.yml')
    with open(yml) as f:
        bugzoo = yaml.load(f, Loader=yaml.FullLoader)
    bug_desc = find_bug_desc(bugzoo['bugs'], program, bug_id)
    if bug_desc == None:
        print("Unknown bug id")

    with open(bug_desc_file, 'w') as f:
        json.dump(bug_desc, f)


def run_docker(args, program, bug_id):
    cmd = [
        'docker', 'run', '-it', '-v',
        "{}:{}".format(LOCALIZER_BIN_DIR,
                       os.path.join(DOCKER_IN_DIR, 'localizer')), '-v',
        "{}:{}".format(SYNTHESIZER_BIN_DIR,
                       os.path.join(DOCKER_IN_DIR, 'synthesizer')), '--mount',
        'type=bind,source={},destination={}'.format(
            bug_desc_file, os.path.join(DOCKER_IN_DIR, 'bug_desc.json'))
    ]
    if args.rm:
        cmd.append('--rm')
    if args.detached:
        cmd.append('-d')
    cmd += ['squareslab/manybugs:{}-{}'.format(program, bug_id), '/bin/bash']
    subprocess.run(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rm', action='store_true')
    parser.add_argument('target', type=str)
    parser.add_argument('-d', action='store_true', dest='detached')
    args = parser.parse_args()
    initialize()
    program = args.target.split('-')[0]
    bug_id = args.target[len(program) + 1:]
    preprocess_bug_desc(program, bug_id)
    run_docker(args, program, bug_id)


if __name__ == '__main__':
    main()
