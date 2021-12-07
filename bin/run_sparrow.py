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
    cmd_args = cmd_str.split()
    try:
        subprocess.call(cmd_args,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
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
        print("[*] Executing: smake for %s" % project + "-" + case)
        run_smake = subprocess.Popen(cmd,
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        PROCS.append(run_smake)
    for proc in PROCS:
        proc.communicate()
        proc.terminate()

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

        if project == "libtiff" and case == "2005-12-21-3b848a7-3edb9cd":
            file = os.path.join(outpath, "parent", "smake-out",
                                "16.015.tif_open.o.i")
            transform(file, "_TIFFmalloc(sizeof (TIFF) + strlen(name) + 1)",
                      "malloc(sizeof (TIFF))")
            file = os.path.join(outpath, "bic", "smake-out",
                                "16.015.tif_open.o.i")
            transform(file, "_TIFFmalloc(sizeof (TIFF) + strlen(name) + 1)",
                      "malloc(sizeof (TIFF))")

        if project == "libtiff" and case == "2007-11-02-371336d-865f7b2":
            file = os.path.join(outpath, "parent", "smake-out",
                                "17.016.tif_open.o.i")
            transform(
                file,
                "_TIFFmalloc((tmsize_t)(sizeof (TIFF) + strlen(name) + 1))",
                "malloc(sizeof (TIFF))")
            file = os.path.join(outpath, "bic", "smake-out",
                                "17.016.tif_open.o.i")
            transform(
                file,
                "_TIFFmalloc((tmsize_t)(sizeof (TIFF) + strlen(name) + 1))",
                "malloc(sizeof (TIFF))")

        if project == "libtiff" and case == "2006-03-03-a72cf60-0a36d7f":
            file = os.path.join(outpath, "parent", "smake-out",
                                "08.007.tif_dirread.o.i")
            transform(
                file,
                "_TIFFCheckMalloc(tif,\n        dircount,\n        sizeof (TIFFDirEntry),\n        \"to read TIFF directory\");",
                "malloc(sizeof(TIFFDirEntry));\n\n\n")
            file = os.path.join(outpath, "bic", "smake-out",
                                "08.007.tif_dirread.o.i")
            transform(
                file,
                "_TIFFCheckMalloc(tif,\n        dircount,\n        sizeof (TIFFDirEntry),\n        \"to read TIFF directory\");",
                "malloc(sizeof(TIFFDirEntry));\n\n\n")
            file = os.path.join(outpath, "bic", "smake-out",
                                "08.007.tif_dirread.o.i")


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
                SPARROW_PATH, "-frontend", "clang", "-skip_main_analysis",
                "-extract_datalog_fact_full_no_opt_dag", "-outdir",
                sparrow_outpath
            ] + target_files
            print("[*] Executing: Sparrow for %s" % project + "-" + case +
                  "-" + version)
            run_sparrow = subprocess.Popen(cmd,
                                           stdout=subprocess.DEVNULL,
                                           stderr=subprocess.DEVNULL)
            PROCS.append(run_sparrow)

    for proc in PROCS:
        proc.communicate()
        proc.terminate()


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
        run_transform(works)
        run_sparrow(works)


if __name__ == '__main__':
    main()
