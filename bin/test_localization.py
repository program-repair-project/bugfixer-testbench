#!/usr/bin/env python3

import argparse
import subprocess
import os
import logging
from datetime import datetime

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RUN_DOCKER_SCRIPT = os.path.join(PROJECT_HOME, 'bin/run-docker.py')
OUT_DIR = os.path.join(PROJECT_HOME, 'localizer-outs')
ENGINE_LIST = ('tarantula', 'prophet')
bug_dict = {}
timestamp = ''

except_case_list = (  # build failure cases list, only regards php projects
        '2011-01-06-e7a1d5004e-3571c955b5','2011-02-19-356b619487-a3a5157286',
        '2011-03-20-2034e14341-7f2937223d','2011-03-25-8138f7de40-3acdca4703',
        '2011-03-26-3acdca4703-c2fe893985','2011-04-06-18d71a6f59-187eb235fe',
        '2011-04-07-77ed819430-efcb9a71cd','2011-04-08-efcb9a71cd-6f3148db81',
        '2011-04-30-9c285fddbb-93f65cdeac','2011-05-13-db0c957f02-8ba00176f1',
        '2011-05-17-453c954f8a-daecb2c0f4','2011-05-21-f5a9e17f9c-964f44a280',
        '2011-05-24-b60f6774dc-1056c57fa9','2011-10-30-c1a4a36c14-5921e73a37',
        '2011-10-31-2e5d5e5ac6-b5f15ef561','2011-11-01-735efbdd04-e0f781f496',
        '2011-11-01-ceac9dc490-9b0d73af1d','2011-11-01-d2881adcbc-4591498df7',
        '2011-11-02-c1d520d19d-9b86852d6e','2011-11-02-de50e98a07-8d520d6296',
        '2011-11-04-9da01ac6b6-7334dfd7eb','2011-11-15-236120d80e-fb37f3b20d',
        '2011-11-16-55acfdf7bd-3c7a573a2c','2011-11-23-eca88d3064-db0888dfc1',
        '2011-12-04-b3ad0b7af7-1d6c98a136','2011-12-10-74343ca506-52c36e60c4',
        '2011-12-17-db63456a8d-3dc9f0abe6','2011-12-18-beda5efd41-622412d8e6',
        '2012-01-13-583292ab22-d74a258f24','2012-01-16-f32760bd40-032d140fd6',
        '2012-02-18-0a91432828-032bbc3164','2012-02-20-0cb26060af-eefefddc0e',
        '2012-02-25-38b549ea2f-1923ecfe25','2012-03-02-730b54a374-1953161b8c',
        '2012-03-04-60dfd64bf2-34fe62619d','2012-03-04-bda5ea7111-60dfd64bf2',
        '2012-03-19-53e3467ff2-9a460497da')


logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def init(args):
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    global timestamp
    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.today().strftime('%Y%m%d-%H:%M:%S')
    bugzoo_process = subprocess.run(['bugzoo', 'bug', 'list'],
                                    capture_output=True,
                                    text=True)
    bugzoo_process.check_returncode()
    bug_list = bugzoo_process.stdout.split('\n')[3:-2]
    for bug in bug_list:
        _, case, _, _, _, installed, _ = list(
            map(lambda s: s.strip(), bug.split('|')))
        case = case.split(':')
        if case[2] in except_case_list:
            continue
        if case[1] in bug_dict:
            bug_dict[case[1]][case[2]] = installed
        else:
            bug_dict[case[1]] = {case[2]: installed}


def build_one(project, case):
    if bug_dict[project][case] == 'Yes':
        logging.info(f'{project}:{case} is already installed. Skip')
    else:
        build_process = subprocess.run(
            ['bugzoo', 'bug', 'build', f'manybugs:{project}:{case}'])
        try:
            build_process.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}:{case} is already installed. Skip')
            return False
        logging.info(f'{project}:{case} is successfully installed')
    return True


def run_one_localizer(project, case, engine):
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
        if image == f'squareslab/manybugs:{project}-{case}':
            docker_id = container_id
            break
    if not docker_id:
        logging.error(f'Cannot find container_id of {project}:{case}')
        return
    # TODO: -skip_compile
    localizer_cmd = [
        'docker', 'exec', '-it', f'{docker_id}',
        '/bugfixer/localizer/main.exe', '-engine', engine, '/experiment'
    ]
    localizer = subprocess.run(localizer_cmd)
    try:
        localizer.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} localizer execution failure')
        return
    out_dir_case = os.path.join(OUT_DIR, project, f'{project}:{case}')
    os.makedirs(out_dir_case, exist_ok=True)
    out_dir_timestamp = os.path.join(out_dir_case, timestamp + '-' + engine)
    cp_cmd = [
        'docker', 'cp', f'{docker_id}:/experiment/localizer-out',
        out_dir_timestamp
    ]
    run_cp = subprocess.run(cp_cmd)
    try:
        run_cp.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(
            f'{project}:{case} localizer executed successfully, but docker cp returns non-zero code'
        )
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


def build_and_run(args):
    project, case, engine = args.project, args.case, args.engine
    if project:
        if case:
            if build_one(project, case):
                if engine:
                    run_one_localizer(project, case, engine)
                else:
                    for engine in ENGINE_LIST:
                        run_one_localizer(project, case, engine)
        else:
            for case in bug_dict[project]:
                if build_one(project, case):
                    if engine:
                        run_one_localizer(project, case, engine)
                    else:
                        for engine in ENGINE_LIST:
                            run_one_localizer(project, case, engine)
    else:
        for project in bug_dict:
            for case in bug_dict[project]:
                if build_one(project, case):
                    if engine:
                        run_one_localizer(project, case, engine)
                    else:
                        for engine in ENGINE_LIST:
                            run_one_localizer(project, case, engine)


def main():
    parser = argparse.ArgumentParser(description='Build bugs using BugZoo.')
    parser.add_argument('-t', '--timestamp', type=str)
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('-e', '--engine', type=str)
    args = parser.parse_args()
    init(args)
    build_and_run(args)


if __name__ == '__main__':
    main()
