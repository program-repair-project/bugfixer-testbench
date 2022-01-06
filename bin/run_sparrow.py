#!/usr/bin/env python3

import os
import subprocess
import argparse
import glob
from benchmark import benchmark
from benchmark import sparrow_custom_option

REPO_NAME = "prosyslab/manybugs-differential"
PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
SMAKE_HOME = os.path.join(PROJECT_HOME, "smake")
SPARROW_PATH = os.path.join(PROJECT_HOME, 'sparrow', 'bin', 'sparrow')
MAX_INSTANCE_NUM = 5


def run_cmd(cmd_str, shell=False):
    if shell:
        cmd_args = cmd_str
    else:
        cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        shell=shell)
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

        print("[*] Executing: smake for %s" % project + "-" + case)
        cmd_str = "docker exec -it %s /experiment/run_smake.sh %s %s" % (
            container, project, case)
        run_cmd(cmd_str)

        outpath = os.path.join(PROJECT_HOME, "output", project, case)

        cmd = "rm -rf %s" % os.path.join(outpath, "bic", "smake-out")
        run_cmd(cmd)
        cmd = "rm -rf %s" % os.path.join(outpath, "parent", "smake-out")
        run_cmd(cmd)
        os.makedirs(outpath, exist_ok=True)

        cmd = "docker cp %s:/experiment/%s/. %s" % (container, project + "-" +
                                                    case, outpath)
        run_cmd(cmd)

        cmd = "docker kill %s" % container
        run_cmd(cmd)


def transform(file, from_text, to_text):
    with open(file, 'rt') as f:
        data = f.read()
        data = data.replace(from_text, to_text)

    with open(file, 'wt') as f:
        f.write(data)


# to handle exceptional cases for sparrow
def run_transform(works):
    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]
        outpath = os.path.join(PROJECT_HOME, "output", project, case)

        if project == "php" and case == "2011-01-18-95388b7cda-b9b1fb1827":
            for ver in ["parent", "bic"]:
                file = os.path.join(outpath, ver, "smake-out",
                                    "0048.apprentice.o.i")
                cmd = "sed '13511,122959d' -i {}".format(file)
                print(cmd)
                run_cmd(cmd, shell=True)
                file = os.path.join(outpath, ver, "smake-out",
                                    "0004.parse_tz.o.i")
                cmd = "sed '5147,22843d' -i {}".format(file)
                run_cmd(cmd, shell=True)
                file = os.path.join(outpath, ver, "smake-out", "010e.zend.o.i")
                cmd = "sed -e 's/alias(\"zend_error\"),//g' -i {}".format(file)
                run_cmd(cmd, shell=True)


def get_target_files(project, case, version):
    smake_outpath = os.path.join(PROJECT_HOME, "output", project, case,
                                 version, "smake-out")
    coverage_file = os.path.join(PROJECT_HOME, "data", "coverage_file",
                                 project, case, "coverage_file.txt")

    target_files = []
    for filename in open(coverage_file, 'r'):
        filename = os.path.splitext(filename.strip())[0]
        target_files += glob.glob(smake_outpath + '/*' + filename + '*.i')

    return target_files


def run_sparrow(works):
    PROCS = []
    for docker_id in works:
        project = docker_id.split('-')[0]
        case = docker_id[len(project) + 1:]

        for version in ["bic", "parent"]:
            smake_outpath = os.path.join(PROJECT_HOME, "output", project, case,
                                         version, "smake-out")

            if project in ["php"]:
                target_files = get_target_files(project, case, version)
            else:
                target_files = glob.glob(smake_outpath + '/*.i')

            sparrow_outpath = os.path.join(PROJECT_HOME, "output", project,
                                           case, version, "sparrow-out")
            os.makedirs(sparrow_outpath, exist_ok=True)
            cmd = [
                SPARROW_PATH, "-extract_datalog_fact_full_no_opt",
                "-skip_main_analysis", "-outdir", sparrow_outpath
            ]
            if project in ["gmp", "libtiff", "php"]:
                cmd += ["-frontend", "cil"]
            else:
                cmd += ["-frontend", "clang"]

            if project in sparrow_custom_option and case in sparrow_custom_option[
                    project]:
                cmd += sparrow_custom_option[project][case]

            benchmark
            cmd += target_files

            print("[*] Executing: Sparrow for %s" % project + "-" + case +
                  "-" + version)

            run_sparrow = subprocess.Popen(cmd,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
            PROCS.append(run_sparrow)

    for proc in PROCS:
        proc.wait()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--project', type=str, default="all")
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('--skip_smake', action='store_true', default=False)
    parser.add_argument('--skip_sparrow', action='store_true', default=False)
    args = parser.parse_args()

    worklist = generate_worklist(args)
    while len(worklist) > 0:
        works = fetch_works(worklist)
        if not args.skip_smake:
            run_smake(works)
            run_transform(works)
        if not args.skip_sparrow:
            run_sparrow(works)
            continue


if __name__ == '__main__':
    main()
