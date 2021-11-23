#!/usr/bin/env python3

import os
import subprocess
import argparse
import csv
import sys
import glob
from datetime import datetime

REPO_NAME = "prosyslab/manybugs-differential"
PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SMAKE_HOME = os.path.join(PROJECT_HOME, "smake")
PROJECT_LIST = ['libtiff']
SPARROW_PATH = os.path.join(PROJECT_HOME, 'sparrow', 'bin', 'sparrow')
MAX_INSTANCE_NUM = 15

timestamp = ''


def init(args):
    global timestamp

    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.today().strftime('%Y%m%d-%H:%M:%S')


def run_cmd(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args)
    except Exception as e:
        print(e)
        exit(1)


def get_cmd_result(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, _ = p.communicate()
        return output
    except Exception as e:
        print(e)
        exit(1)


def generate_worklist(projects):
    worklist = []
    for project in projects:
        dockers = subprocess.check_output(['docker', 'images']).decode('utf-8')
        dockers = dockers.split("\n")

        for d in dockers:
            if project in d and "differential" in d:
                _, docker_id = d.split()[:2]
                worklist.append(docker_id)

    return worklist


def fetch_works(worklist):
    works = []
    for i in range(MAX_INSTANCE_NUM):
        if len(worklist) <= 0:
            break
        works.append(worklist.pop(0))
    return works


def run_smake(works):

    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]

        image_name = REPO_NAME + ":" + docker_id
        container = docker_id + "-smake"
        cmd = "docker run --rm -it -v %s:%s -d --name %s %s /bin/bash" % (
            SMAKE_HOME, "/bugfixer/smake", container, image_name)
        run_cmd(cmd)

        smake_script_path = os.path.join(PROJECT_HOME, "bin", "run_smake.sh")
        cmd = "docker cp %s %s:/experiment/run_smake.sh " % (smake_script_path,
                                                             container)
        run_cmd(cmd)

    ## run smake in parallel
    PROCS = []
    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]
        container = docker_id + "-smake"

        cmd = [
            "docker", "exec", "-it", container, "/experiment/run_smake.sh",
            project
        ]
        run_sparrow = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        PROCS.append(run_sparrow)
    for proc in PROCS:
        proc.communicate()

    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]
        container = docker_id + "-smake"

        smake_outpath = os.path.join(PROJECT_HOME, "output", "smake-out",
                                     project, case)

        cmd = "rm -r %s" % smake_outpath
        run_cmd(cmd)

        os.makedirs(smake_outpath, exist_ok=True)
        cmd = "docker cp %s:/experiment/smake-out/bic %s" % (container,
                                                             smake_outpath)
        run_cmd(cmd)
        cmd = "docker cp %s:/experiment/smake-out/parent %s" % (container,
                                                                smake_outpath)
        run_cmd(cmd)

        cmd = "docker kill %s" % container
        run_cmd(cmd)


def run_sparrow(works):
    PROCS = []
    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]

        for version in ["bic", "parent"]:
            smake_outpath = os.path.join(PROJECT_HOME, "output", "smake-out",
                                         project, case, version)
            target_files = glob.glob(smake_outpath + '/*.i')

            sparrow_outpath = os.path.join(PROJECT_HOME, "output",
                                           "sparrow-outs", project, case,
                                           timestamp, version)
            os.makedirs(sparrow_outpath, exist_ok=True)
            cmd = [
                SPARROW_PATH, "-frontend", "clang",
                "-extract_datalog_fact_full_no_opt", "-outdir", sparrow_outpath
            ] + target_files

            run_sparrow = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            PROCS.append(run_sparrow)

    for proc in PROCS:
        proc.communicate()


def main():
    parser = argparse.ArgumentParser(description='Build bugs using BugZoo.')
    parser.add_argument('-t', '--timestamp', type=str)
    parser.add_argument('-p', '--project', type=str, default="all")
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('--skip_smake', action='store_true', default=False)
    args = parser.parse_args()

    init(args)

    if args.project == "all":
        projects = PROJECT_LIST
    else:
        projects = [args.project]

    if args.case:
        worklist = [args.project + "-" + args.case]
    else:
        worklist = generate_worklist(projects)

    while len(worklist) > 0:
        works = fetch_works(worklist)
        if not args.skip_smake:
            run_smake(works)
        run_sparrow(works)


if __name__ == '__main__':
    main()
