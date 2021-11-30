#!/usr/bin/env python3

import os
import subprocess
import argparse
import glob
from benchmark import benchmark

REPO_NAME = "prosyslab/manybugs-differential"
PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SMAKE_HOME = os.path.join(PROJECT_HOME, "smake")
SPARROW_PATH = os.path.join(PROJECT_HOME, 'sparrow', 'bin', 'sparrow')
MAX_INSTANCE_NUM = 2


def run_cmd(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args)
    except Exception as e:
        print(e)
        exit(1)


def generate_worklist(args):
    worklist = []
    if (args.project == "all"):
        for project in benchmark:
            for case in benchmark[project]:
                worklist.append(project + "-" + case)
    else:
        if (args.case):
            worklist.append(args.project + "-" + args.case)
        else:
            for case in benchmark[args.project]:
                worklist.append(args.project + "-" + case)

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
            project, case
        ]
        print("[*] Executing: %s" % " ".join(cmd))
        run_smake = subprocess.Popen(cmd,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        PROCS.append(run_smake)
    for proc in PROCS:
        proc.communicate()

    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]
        container = docker_id + "-smake"

        outpath = os.path.join(PROJECT_HOME, "output", project, case)

        cmd = "rm -rf %s" % outpath
        run_cmd(cmd)
        os.makedirs(outpath, exist_ok=True)

        cmd = "docker cp %s:/experiment/%s/. %s" % (container, project + "-" +
                                                    case, outpath)
        run_cmd(cmd)

        cmd = "docker kill %s" % container
        run_cmd(cmd)


def run_sparrow(works):
    PROCS = []
    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]

        for version in ["bic", "parent"]:
            smake_outpath = os.path.join(PROJECT_HOME, "output", project, case,
                                         version, "smake-out")
            target_files = glob.glob(smake_outpath + '/*.i')

            sparrow_outpath = os.path.join(PROJECT_HOME, "output", project,
                                           case, version, "sparrow-out")
            os.makedirs(sparrow_outpath, exist_ok=True)
            cmd = [
                SPARROW_PATH, "-frontend", "clang",
                "-extract_datalog_fact_full_no_opt_dag", "-outdir",
                sparrow_outpath
            ]
            print("[*] Executing: %s ./*.i" % " ".join(cmd))
            run_sparrow = subprocess.Popen(cmd + target_files,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
            PROCS.append(run_sparrow)

    for proc in PROCS:
        proc.communicate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', type=str, default="all")
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('--skip_smake', action='store_true', default=False)
    args = parser.parse_args()

    worklist = generate_worklist(args)
    while len(worklist) > 0:
        works = fetch_works(worklist)
        if not args.skip_smake:
            run_smake(works)
        run_sparrow(works)


if __name__ == '__main__':
    main()
