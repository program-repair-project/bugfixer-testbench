#!/usr/bin/env python3

import argparse
import os
import logging
import sys
import subprocess
from test_localization import bug_dict, except_case_list, init

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(PROJECT_HOME, 'localizer-outs')

DOCKER_IN_DIRECTORY = '/unival'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def initialize(args):
    if not os.path.isdir(OUT_DIR):
        logging.error(
            'There is no output directory. Run UniVal Frontend first.')
        sys.exit()
    init(args)


def run_one(project, case, timestamp):
    name_of_timestamp = timestamp.replace(':', '-')
    docker_run_cmd = [
        'docker', 'run', '-it', '-d', '--name',
        f'{project}-{case}-{name_of_timestamp}', 'unival', '/bin/bash'
    ]
    docker_run = subprocess.run(docker_run_cmd)
    try:
        docker_run.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} docker run failed')

    docker_ps = subprocess.run(['docker', 'ps'],
                               capture_output=True,
                               text=True)
    docker_ps.check_returncode()
    dockers = docker_ps.stdout.split('\n')[1:]
    docker_id = None
    for d in dockers:
        column = d.split()
        container_id = column[0]
        image = column[1]
        name = column[-1]
        if image == 'unival' and name == f'{project}-{case}-{name_of_timestamp}':
            docker_id = container_id
            break
    if not docker_id:
        logging.error(f'Cannot find container_id of {project}:{case}')
        return

    for java_file in [
            'StructuredDataCollector.java', 'ProcessDataProfile.java'
    ]:
        javac_cmd = [
            'docker', 'exec', '-it', f'{docker_id}', 'javac', java_file
        ]
        javac = subprocess.run(javac_cmd)
        try:
            javac.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}:{case} java compile failed')

    DATA_PATH = os.path.join(OUT_DIR, project, f'{project}:{case}',
                             f'{timestamp}-unival')

    for data_file in ['CausalMap.txt', 'FaultCandidates.txt', 'output.txt']:
        cp_cmd = [
            'docker', 'cp',
            os.path.join(DATA_PATH, data_file), f'{docker_id}:/unival/'
        ]
        cp = subprocess.run(cp_cmd)
        try:
            cp.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}:{case} docker cp failed')

    java_cmd = [
        'docker', 'exec', '-it', f'{docker_id}', 'java', 'ProcessDataProfile'
    ]
    java = subprocess.run(java_cmd)
    try:
        java.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} ProcessDataProfile failed')

    mkdir_cmd = [
        'docker', 'exec', '-it', f'{docker_id}', 'mkdir', '-p', 'NUMFL'
    ]
    mkdir = subprocess.run(mkdir_cmd)
    try:
        mkdir.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} mkdir failed')

    r_cmd = ['docker', 'exec', '-it', f'{docker_id}', 'Rscript', 'RFC.R', '0']
    r = subprocess.run(r_cmd)
    try:
        r.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} RFC failed')

    cp_cmd = ['docker', 'cp', f'{docker_id}:/unival/', f'{DATA_PATH}/']
    cp = subprocess.run(cp_cmd)
    try:
        cp.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} cp output failed')

    stop_cmd = ['docker', 'stop', f'{docker_id}']
    stop = subprocess.run(stop_cmd)
    try:
        stop.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'Cannot stop docker container of {project}:{case}')
    rm_cmd = ['docker', 'rm', f'{docker_id}']
    rm = subprocess.run(rm_cmd)
    try:
        rm.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'Cannot remove docker continer of {project}:{case}')


def run(args):
    project, case, timestamp = args.project, args.case, args.timestamp
    if project:
        if case:
            run_one(project, case, timestamp)
        else:
            for case in bug_dict[project]:
                run_one(project, case, timestamp)
    else:
        for project in bug_dict:
            for case in bug_dict[project]:
                run_one(project, case, timestamp)


def main():
    parser = argparse.ArgumentParser(description='UniVal Backend.')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('timestamp', type=str)
    args = parser.parse_args()
    initialize(args)
    run(args)


if __name__ == '__main__':
    main()
