#!/usr/bin/env python3

import argparse
import subprocess
import os

PATH = os.getcwd()
RUN_DOCKER_SCRIPT = os.path.join(PATH, 'bin/run-docker.py')
OUT_DIR = os.path.join(PATH, 'localizer-outs')
bug_dict = {}

def init():
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    bugzoo_process = subprocess.run(['bugzoo', 'bug', 'list'], capture_output=True, text=True)
    bugzoo_process.check_returncode()
    bug_list = bugzoo_process.stdout.split('\n')[3:-2]
    for bug in bug_list:
        _, case, _, _, _, installed, _ = list(map(lambda s: s.strip(), bug.split('|')))
        case = case.split(':')
        if case[1] in bug_dict:
            bug_dict[case[1]][case[2]] = installed
        else:
            bug_dict[case[1]] = {case[2]: installed}

def build_one(project, case):
    if bug_dict[project][case] == 'Yes':
        print(f'{project}:{case} is already installed. Skip')
    else:
        build_process = subprocess.run(['bugzoo', 'bug', 'build', f'manybugs:{project}:{case}'])
        build_process.check_returncode()
        print(f'[{project}:{case}] Succesfully installed.')

def build(project, case):
    if project:
        if case:
            build_one(project, case)
        else:
            for case in bug_dict[project]:
                build_one(project, case)
    else:
        for project in bug_dict:
            for case in bug_dict[project]:
                build_one(project, case)

def run_one_localizer(project, case):
    cmd = [f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d']
    run_docker = subprocess.run(cmd)
    run_docker.check_returncode()
    docker_ps = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
    docker_ps.check_returncode()
    dockers = docker_ps.stdout.split('\n')[1:]
    docker_id = None
    for d in dockers:
        container_id, image = d.split()[:2]
        if image == f'squareslab/manybugs:{project}-{case}':
            docker_id = container_id
            break
    if not docker_id:
        print('Cannot find container_id')
        return
    # TODO: -skip_compile
    localizer_cmd = ['docker', 'exec', '-it', f'{docker_id}', '/bugfixer/localizer/main.exe', '/experiment']
    localizer = subprocess.run(localizer_cmd)
    # TODO: use logger
    print(f'[{project}:{case}] localizer return_code: {localizer.returncode}')
    try:
        localizer.check_returncode()
    except subprocess.CalledProcessError:
        return
    cp_cmd = ['docker', 'cp', f'{docker_id}:/experiment/localizer-out', f'{OUT_DIR}/{project}:{case}']
    run_cp = subprocess.run(cp_cmd)
    try:
        run_cp.check_returncode()
    except subprocess.CalledProcessError:
        print('[{project}:{case}] localizer executed successfully, but docker cp returns non-zero code')

def run_localizer(project, case):
    if project:
        if case:
            run_one_localizer(project, case)
        else:
            for case in bug_dict[project]:
                run_one_localizer(project, case)
    else:
        for project in bug_dict:
            for case in bug_dict[project]:
                run_one_localizer(project, case)
                    
def main():
    parser = argparse.ArgumentParser(description='Build bugs using BugZoo.')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    args = parser.parse_args()
    init()
    build(args.project, args.case)
    run_localizer(args.project, args.case)


if __name__ == '__main__':
    main()
