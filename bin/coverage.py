#!/usr/bin/env python3

import argparse
from asyncio.subprocess import DEVNULL
import subprocess
import os
import logging
from benchmark import benchmark, faulty_function
from pathlib import Path

PROJECT_HOME = Path(__file__).resolve().parent.parent
RUN_DOCKER_SCRIPT = PROJECT_HOME / 'bin/run-docker-differential.py'
OUTPUT_DIR = PROJECT_HOME / 'output'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def extract_one_coverage(args, project, case, engine, is_faulty_func=False):
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

    BIC_PATH = OUTPUT_DIR / project / case / 'bic' / 'sparrow-out'
    PARENT_PATH = OUTPUT_DIR / project / case / 'parent' / 'sparrow-out'
    PARENT_COV_PATH = PARENT_PATH / 'coverage.txt'

    if engine == 'unival':
        if not ((BIC_PATH / 'coverage_tarantula.txt').exists()
                and PARENT_COV_PATH.exists()):
            logging.info(
                "There is no coverage file. Start extracting it first (using tarantula)."
            )
            extract_one_coverage(args, project, case, 'tarantula',
                                 is_faulty_func)

    print("[*] Extracting coverage of : %s-%s" % (project, case))

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

    # copy file and scripts
    if is_faulty_func:
        ff_path = OUTPUT_DIR / project / case / 'faulty_func.txt'
        with ff_path.open(mode='w') as fff:
            fff.writelines(
                map(lambda s: s + '\n', faulty_function[project][case]))
        run_cmd_and_check(
            ['docker', 'cp',
             str(ff_path), f'{docker_id}:/experiment/'])
    run_cmd_and_check(
        ['docker', 'cp', './bin/line_matching.py', f'{docker_id}:/experiment'],
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
    elif project == 'php':
        run_cmd_and_check([
            'docker', 'cp', './bin/transform_php.sh',
            f'{docker_id}:/experiment'
        ])
        run_cmd_and_check(
            ['docker', 'exec', docker_id, '/experiment/transform_php.sh'])
        if case in [
                "2011-01-18-95388b7cda-b9b1fb1827",
                "2011-02-21-2a6968e43a-ecb9d8019c",
                "2011-03-11-d890ece3fc-6e74d95f34",
                "2011-03-27-11efb7295e-f7b7b6aa9e",
                "2011-04-07-d3274b7f20-77ed819430"
        ]:
            cmd = [
                'docker', 'cp', './bin/parent_checkout_php_a.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
        elif case in [
                "2011-10-31-c4eb5f2387-2e5d5e5ac6",
                "2011-11-08-0ac9b9b0ae-cacf363957",
                "2011-12-04-1e6a82a1cf-dfa08dc325"
        ]:
            cmd = [
                'docker', 'cp', './bin/parent_checkout_php_b.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
        elif case in [
                "2011-11-19-eeba0b5681-f330c8ab4e",
                "2012-03-08-0169020e49-cdc512afb3"
        ]:
            cmd = [
                'docker', 'cp', './bin/parent_checkout_php_c.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
        elif case in [
                "2012-03-12-7aefbf70a8-efc94f3115",
                "2011-11-11-fcbfbea8d2-c1e510aea8",
                "2011-11-08-c3e56a152c-3598185a74"
        ]:
            cmd = [
                'docker', 'cp', './bin/parent_checkout_php_d.sh',
                f'{docker_id}:/experiment/parent_checkout.sh'
            ]
            run_cmd_and_check(cmd,
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    elif project in ['grep', 'tar', 'readelf', 'shntool', 'sed']:
        pass
    else:
        raise Exception(f'{project}-{case} is not supported currently')

    # run localizer
    if project == 'php':
        cmd = [
            'docker', 'exec', f'{docker_id}', '/bugfixer/localizer/main.exe',
            '-engine', engine, '-bic', '-no_seg', '.'
        ]
    elif project in ['grep', 'tar', 'readelf', 'shntool', 'sed']:
        cmd = [
            'docker', 'exec', f'{docker_id}', '/bugfixer/localizer/main.exe',
            '-engine', engine, '-bic', '-gcov', '.'
        ]
    else:
        cmd = [
            'docker', 'exec', f'{docker_id}', '/bugfixer/localizer/main.exe',
            '-engine', engine, '-bic', '.'
        ]
    if is_faulty_func:
        cmd += ['-faulty_func']
    if args.gcov:
        cmd += ['-gcov']
    run_cmd_and_check(cmd)

    # make output directories
    BIC_PATH.mkdir(parents=True, exist_ok=True)
    PARENT_PATH.mkdir(parents=True, exist_ok=True)
    (PROJECT_HOME / 'data' / 'coverage_file' / project / case).mkdir(
        parents=True, exist_ok=True)

    # copy output data
    if engine == 'unival':
        run_cmd_and_check([
            'docker', 'cp', f'{docker_id}:/experiment/localizer-out',
            str(OUTPUT_DIR / project / case / 'unival')
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)
    else:
        engine_list = []
        if engine == 'all':
            engine_list = ["prophet", "ochiai", "jaccard", "tarantula"]
        else:
            engine_list.append(engine)

        cov_file_list = []
        for e in engine_list:
            cov_file_list.append(('localizer-out/coverage_' + e + '_bic.txt',
                                  'bic/sparrow-out/coverage_' + e + '.txt'))

        for from_file, to_file in (cov_file_list + [
            ('localizer-out/coverage_parent.txt',
             'parent/sparrow-out/coverage.txt'),
            ('line_matching.json', 'bic/sparrow-out/line-matching.json'),
        ]):
            run_cmd_and_check([
                'docker', 'cp', f'{docker_id}:/experiment/{from_file}',
                str(OUTPUT_DIR / project / case / to_file)
            ],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        run_cmd_and_check([
            'docker', 'cp',
            f'{docker_id}:/experiment/localizer-out/coverage_file.txt',
            str(PROJECT_HOME / 'data' / 'coverage_file' / project / case /
                'coverage_file.txt')
        ],
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL)

    # docker stop and rm
    run_cmd_and_check(['docker', 'stop', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
    run_cmd_and_check(['docker', 'rm', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)


def extract_coverage(args):
    project, case, engine, is_faulty_func = args.project, args.case, args.engine, args.faulty_func

    if project:
        if case:
            extract_one_coverage(args, project, case, engine, is_faulty_func)
        else:
            for case in benchmark[project]:
                extract_one_coverage(args, project, case, engine,
                                     is_faulty_func)
    else:
        for project in benchmark:
            for case in benchmark[project]:
                extract_one_coverage(args, project, case, engine,
                                     is_faulty_func)


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
    parser.add_argument('-f',
                        '--faulty_func',
                        action='store_true',
                        default=False)
    parser.add_argument('-g', '--gcov', action='store_true', default=False)
    args = parser.parse_args()
    extract_coverage(args)


if __name__ == '__main__':
    main()
