#!/usr/bin/env python3

import argparse
import subprocess
import os
import logging
from benchmark import benchmark

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RUN_DOCKER_SCRIPT = os.path.join(PROJECT_HOME,
                                 'bin/run-docker-differential.py')
OUTPUT_DIR = os.path.join(PROJECT_HOME, 'output')


def get_one_coverage(project, case):
    #run docker
    cmd = [f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d']
    run_docker = subprocess.run(cmd)
    run_docker.check_returncode()
    docker_ps = subprocess.run(['docker', 'ps'],
                               capture_output=True,
                               text=True)
    docker_ps.check_returncode()
    dockers = docker_ps.stdout.split('\n')[1:]
    docker_id = None
    for d in dockers:
        container_id, image = d.split()[:2]
        if image == f'prosyslab/manybugs-differential:{project}-{case}':
            docker_id = container_id
            break
    if not docker_id:
        logging.error(f'Cannot find container_id of {project}:{case}')
        return

    # copy scripts
    cmd = [
        'docker', 'cp', './bin/line_matching.py', f'{docker_id}:/experiment'
    ]
    copy = subprocess.run(cmd)
    try:
        copy.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} copy failure')

    if project == 'libtiff':
        cmd = [
            'docker', 'cp', './bin/parent_checkout.sh',
            f'{docker_id}:/experiment'
        ]
    else:
        raise Exception(f'{project} is not supported currently')
    copy = subprocess.run(cmd)
    try:
        copy.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} copy failure')

    # run localizer
    cmd = [
        'docker', 'exec', f'{docker_id}', '/bugfixer/localizer/main.exe',
        '-engine', 'tarantula', 'bic', '.'
    ]
    localize = subprocess.run(cmd)
    try:
        localize.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} localize failure')

    # copy coverage data
    cmd = [
        'docker', 'cp',
        f'{docker_id}:/experiment/localizer-out/coverage_diff.txt',
        f'{OUTPUT_DIR}/{project}/{case}/coverage.txt'
    ]
    copy = subprocess.run(cmd)
    try:
        copy.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} coverage_diff copy failure')

    cmd = [
        'docker', 'cp',
        f'{docker_id}:/experiment/localizer-out/coverage_bic.txt',
        f'{OUTPUT_DIR}/{project}/{case}/bic/coverage.txt'
    ]
    copy = subprocess.run(cmd)
    try:
        copy.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} coverage_bic copy failure')

    cmd = [
        'docker', 'cp',
        f'{docker_id}:/experiment/localizer-out/coverage_parent.txt',
        f'{OUTPUT_DIR}/{project}/{case}/parent/coverage.txt'
    ]
    copy = subprocess.run(cmd)
    try:
        copy.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} coverage_parent copy failure')

    # docker kill
    cmd = ['docker', 'kill', f'{docker_id}']
    kill = subprocess.run(cmd)
    try:
        kill.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}-{case} docker kill failure')


def get_coverage(args):
    project, case = args.project, args.case

    if project:
        if case:
            get_one_coverage(project, case)
        else:
            for case in benchmark[project]:
                get_one_coverage(project, case)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                get_one_coverage(project, case)


def main():
    parser = argparse.ArgumentParser(
        description='Get coverage data of project-case')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    args = parser.parse_args()
    get_coverage(args)


if __name__ == '__main__':
    main()
