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

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def run_one_observe(project, case, engine):
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

    print("[*] Extracting observation of : %s-%s" % (project, case))

    # run docker
    run_cmd_and_check([f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    # find docker container ID
    docker_ps = run_cmd_and_check(['docker', 'ps'],
                                  capture_output=True,
                                  text=True)
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
    if engine != 'unival':
        run_cmd_and_check([
            'docker', 'cp', './bin/line_matching.py',
            f'{docker_id}:/experiment'
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

        if project == 'libtiff':
            cmd = [
                'docker', 'cp', './bin/parent_checkout_libtiff.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
        elif project == 'gmp':
            cmd = [
                'docker', 'cp', './bin/parent_checkout_gmp.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
        else:
            raise Exception(f'{project} is not supported currently')
        run_cmd_and_check(cmd,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

    # run localizer
    run_cmd_and_check([
        'docker', 'exec', f'{docker_id}', '/bugfixer/localizer/main.exe',
        '-engine', engine, '-bic', '.'
    ],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    # copy output data
    if engine == 'unival':
        run_cmd_and_check([
            'docker', 'cp', f'{docker_id}:/experiment/localizer-out',
            f'{OUTPUT_DIR}/{project}/{case}/unival'
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    else:
        for from_file, to_file in [
            ('localizer-out/coverage_bic.txt', 'bic/sparrow-out/coverage.txt'),
            ('localizer-out/coverage_parent.txt',
             'parent/sparrow-out/coverage.txt'),
            ('line_matching.json', 'bic/sparrow-out/line-matching.json'),
        ]:
            run_cmd_and_check([
                'docker', 'cp', f'{docker_id}:/experiment/{from_file}',
                f'{OUTPUT_DIR}/{project}/{case}/{to_file}'
            ],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)

    # docker kill
    run_cmd_and_check(['docker', 'kill', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    # run unival_backend if engine is unival
    if engine == 'unival':
        run_cmd_and_check([
            f'{PROJECT_HOME}/bin/unival_backend.py', '-p', project, '-c', case
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)


def run_observe(args):
    project, case, engine = args.project, args.case, args.engine

    if project:
        if case:
            run_one_observe(project, case, engine)
        else:
            for case in benchmark[project]:
                run_one_observe(project, case, engine)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                run_one_observe(project, case, engine)


def main():
    parser = argparse.ArgumentParser(
        description='Get coverage data of project-case')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument(
        '-e',
        '--engine',
        type=str,
        choices=['tarantula', 'ochiai', 'jaccard', 'prophet', 'unival', 'all'],
        default='tarantula')
    args = parser.parse_args()
    run_observe(args)


if __name__ == '__main__':
    main()
