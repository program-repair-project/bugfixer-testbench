#!/usr/bin/env python3

import argparse
import os
import logging
import subprocess
from benchmark import benchmark

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
OUT_DIR = os.path.join(PROJECT_HOME, 'output')

DOCKER_IN_DIRECTORY = '/unival'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def run_one(project, case):
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

    # run docker container
    run_cmd_and_check([
        'docker', 'run', '-it', '-d', '--name', f'{project}-{case}', 'unival',
        '/bin/bash'
    ],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    # find docker container ID
    docker_ps = run_cmd_and_check(['docker', 'ps'],
                                  capture_output=True,
                                  text=True)
    dockers = docker_ps.stdout.split('\n')[1:]
    docker_id = None
    for d in dockers:
        column = d.split()
        container_id = column[0]
        image = column[1]
        name = column[-1]
        if image == 'unival' and name == f'{project}-{case}':
            docker_id = container_id
            break
    if not docker_id:
        logging.error(f'Cannot find container_id of {project}:{case}')
        return

    # compile java codes
    for java_file in [
            'StructuredDataCollector.java', 'ProcessDataProfile.java'
    ]:
        run_cmd_and_check(
            ['docker', 'exec', '-it', docker_id, 'javac', java_file])

    # copy data files into docker container
    DATA_PATH = os.path.join(OUT_DIR, project, case, 'unival')

    for data_file in ['CausalMap.txt', 'FaultCandidates.txt', 'output.txt']:
        run_cmd_and_check([
            'docker', 'cp',
            os.path.join(DATA_PATH, data_file), f'{docker_id}:/unival/'
        ])

    # run java
    run_cmd_and_check(
        ['docker', 'exec', '-it', docker_id, 'java', 'ProcessDataProfile'])

    # run Rscript
    run_cmd_and_check(
        ['docker', 'exec', '-it', docker_id, 'mkdir', '-p', 'NUMFL'])
    run_cmd_and_check(
        ['docker', 'exec', '-it', docker_id, 'Rscript', 'RFC.R', '0'])

    # copy result directory to out_dir
    run_cmd_and_check(
        ['docker', 'cp', f'{docker_id}:/unival/', f'{DATA_PATH}/'])

    # docker kill
    run_cmd_and_check(['docker', 'kill', docker_id])


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
    parser = argparse.ArgumentParser(description='UniVal Backend.')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    args = parser.parse_args()
    if not os.path.isdir(OUT_DIR):
        logging.error(
            'There is no output directory. Run UniVal Frontend first.')
        return
    run(args)


if __name__ == '__main__':
    main()
