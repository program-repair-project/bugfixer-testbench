#!/usr/bin/env python3

from parse import *
import os
from pathlib import Path
import subprocess
from asyncio.subprocess import DEVNULL
import logging
import multiprocessing
import parmap
import json
from tqdm import tqdm


PROJECT_HOME = Path(__file__).resolve().parent.parent
DATA_DIR = Path('/data/jongchan/')
COVERAGE_DIR = DATA_DIR / 'blazer_all_output'
OUTPUT_DIR = DATA_DIR / 'blazer_all_output'

RUN_DOCKER_SCRIPT = PROJECT_HOME / 'bin/run-docker.py'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")



def inject_assertion(run_info):
    project, case, inject_file, inject_line, assertion_filepath, cpu_count = run_info
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

    print("[*] Injecting assert of : %s-%s-%s-%s" % (project, case, inject_file, str(inject_line)))

    # run docker
    cmd = [f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d', '--rm', '--name', f'{project}-{case}-{inject_file}-{inject_line}-assert']
    cmd = cmd + ['--cpuset-cpus'] + [f'{cpu_count*2}-{cpu_count*2+1}'] if cpu_count != None else cmd
    run_cmd_and_check(cmd,
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    # find docker container ID
    # docker_ps = run_cmd_and_check(['docker', 'ps'],
    #                               capture_output=True,
    #                               text=True)
    # dockers = docker_ps.stdout.split('\n')[1:]
    # docker_id = None
    # for d in dockers:
    #     container_id, image = d.split()[:2]
    #     if image == f'prosyslab/manybugs:{project}-{case}':
    #         docker_id = container_id
    #         break
    # if not docker_id:
    #     logging.error(f'Cannot find container_id of {project}:{case}')
    #     return
    docker_id = f'{project}-{case}-{inject_file}-{inject_line}-assert'

    run_cmd_and_check(
        ['docker', 'cp', f'{assertion_filepath}', f'{docker_id}:/experiment'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

    run_cmd_and_check(
        ['docker', 'exec', docker_id, '/bugfixer/localizer/main.exe', '-engine', 'assert', '-inject_file', inject_file, '-inject_line', inject_line, '.'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    
    run_cmd_and_check(
        ['docker', 'cp', f'{docker_id}:/experiment/localizer-out/result_ochiai_assert.txt', f"{str(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line)}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

    run_cmd_and_check(['docker', 'kill', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)


def is_empty_assertion(assertion_filepath):
    
    with open(assertion_filepath) as assertion_file:
        assertion_json = json.load(assertion_file)
    
        for test_type in assertion_json:
            if test_type!="neg":
                continue
            value_num = 0
            for tc in assertion_json[test_type]:
                for var in assertion_json[test_type][tc]:
                    value_num += len(assertion_json[test_type][tc][var])
            if value_num == 0:
                return True
    return False


def read_signal_list(signal_list_file):
    result = []
    for line in signal_list_file:
        parse_line = parse("{}:{}\t{} {} {}", line.strip())
        if parse_line != None:
            result.append((parse_line[0], parse_line[1], parse_line[4]))
    return result
  


def main():
    num_cores = multiprocessing.cpu_count()
    work_list = []
    for project in os.listdir(COVERAGE_DIR):
        for case in os.listdir(COVERAGE_DIR / project):
            if not os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                continue
            signal_list_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'result_signal_filter.txt')
            signal_list = read_signal_list(signal_list_file)
            signal_list_file.close()
            signal_list_neg_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'result_signal_neg_filter.txt')
            signal_list_neg = read_signal_list(signal_list_neg_file)
            signal_list_neg_file.close()
            
            signal_list += signal_list_neg
            for inject_file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                if inject_file in ['tmp', 'tmp2']:
                    continue
                if inject_file.startswith('tmp_value_'):
                    continue
                for inject_line in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file):
                    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "result_ochiai_assert.txt"):
                        continue
                    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt") and os.path.getsize(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt") > 2:
                        assertion_filepath = COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt"
                        if is_empty_assertion(assertion_filepath):
                            continue
                        if len(list(filter(lambda x: inject_file in x[0] and inject_line in x[1] and float(x[2]) >= 0.5, signal_list)))> 0:
                            work_list.append((project, case, inject_file, inject_line, assertion_filepath))
                            
    num_process = 30
    split_work_list=[work_list[y-num_process:y] for y in range(num_process, len(work_list)+num_process,num_process)]
    for wl in tqdm(split_work_list):
        run_info = list(map(lambda x: (x[1][0], x[1][1], x[1][2], x[1][3], x[1][4], x[0]), enumerate(wl)))
        parmap.map(inject_assertion, run_info, pm_pbar=True, pm_processes=num_process)



if __name__ == '__main__':
    main()