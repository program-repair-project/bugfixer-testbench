#!/usr/bin/env python3

import argparse
from parse import *
import os
import yaml
from pathlib import Path
import subprocess
from asyncio.subprocess import DEVNULL
import logging
import multiprocessing
import parmap
from tqdm import tqdm

PROJECT_HOME = Path(__file__).resolve().parent.parent
DATA_DIR = Path('/data/jongchan')
COVERAGE_DIR = DATA_DIR / 'blazer_all_output'
OUTPUT_DIR = DATA_DIR / 'blazer_all_output'
YML_DIR = PROJECT_HOME / 'benchmark'

RUN_DOCKER_SCRIPT = PROJECT_HOME / 'bin/run-docker.py'

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")

def read_signal(signal_filename):
    signal_list = dict()
    with open(signal_filename) as signal_file:
        before, after = None, None
        for i, line in enumerate(signal_file):
            parse_line = parse("{}:{}\t{} {}", line.strip())
            if parse_line != None:
                file, line, neg, pos = parse_line[0], parse_line[1], parse_line[2], parse_line[3]
                signal = (line, neg, pos)
                if file not in signal_list:
                    signal_list[file] = []
                signal_list[file].append(signal)
    return signal_list



def get_test_num(project, case):
    with open(os.path.join(YML_DIR, project, f'{project}.bugzoo.yml')) as f:
        bug_data = yaml.load(f, Loader=yaml.FullLoader)
        neg_num = 0
        pos_num = 0
        for data in bug_data['bugs']:
            if data['name'].split(':')[-1] == case:
                neg_num = int(data['test-harness']['failing'])
                pos_num = int(data['test-harness']['passing'])
                break
        else:
            raise Exception("TEST NUM NOT FOUND")
    return neg_num, pos_num



def extract_one_signal(run_info):
    project, case, signal_list, cpu_count= run_info
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

    print("[*] Extracting value of : %s-%s" % (project, case))

    VALUE_DIR = Path(f'/data/jongchan/blazer_all_output/{project}/{case}/bic/sparrow-out/value')
    os.makedirs(VALUE_DIR, exist_ok=True)

    # run docker
    cmd = [f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d', '--rm', '--name', f'{project}-{case}-value', '--outdir', VALUE_DIR]
    cmd = cmd + ['--cpuset-cpus'] + [f'{cpu_count*4}-{cpu_count*4+3}'] if cpu_count != None else cmd
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
    docker_id = f'{project}-{case}-value'

    for (sig_file, sig_line) in signal_list:
        run_cmd_and_check(
            ['docker', 'exec', docker_id, 'bash', '-c', f"echo {sig_file}:{sig_line} >> /experiment/signal_list.txt"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

    run_cmd_and_check(
        ['docker', 'exec', docker_id, '/bugfixer/localizer/main.exe', '-engine', 'value_print', '.'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    
    neg_num, pos_num = get_test_num(project, case)

    for i in range(neg_num):
        run_cmd_and_check(
        ['docker', 'cp', f'{docker_id}:/experiment/output_n{i+1}.txt', str(VALUE_DIR / f'tmp_value_n{i+1}.txt')],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    
    # for i in range(pos_num):
    #     run_cmd_and_check(
    #     ['docker', 'cp', f'{docker_id}:/experiment/output_p{i+1}.txt', str(VALUE_DIR / f'tmp_value_p{i+1}.txt')],
    #     stdout=subprocess.DEVNULL,
    #     stderr=subprocess.DEVNULL)

    run_cmd_and_check(['docker', 'stop', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)
    
    for i in range(neg_num):
        if os.path.exists(VALUE_DIR / f'tmp_value_n{i+1}.txt'):
            with open(VALUE_DIR / f'tmp_value_n{i+1}.txt', encoding='ISO-8859-1') as tmp_value_file:
                for line in tmp_value_file:
                    parse_line = parse("{}:{},{},{}", line.strip())
                    if parse_line != None:
                        sig_file, sig_line, v_name, value = os.path.basename(parse_line[0]), parse_line[1], parse_line[2], parse_line[3]
                        SIG_DIR = VALUE_DIR / sig_file / sig_line
                        os.makedirs(SIG_DIR, exist_ok=True)
                        with open(SIG_DIR / f'value_n{i+1}.txt', 'a') as value_file:
                            value_file.write(f'{v_name},{value}\n')

    # for i in range(pos_num):
    #     if os.path.exists(VALUE_DIR / f'tmp_value_p{i+1}.txt'):
    #         with open(VALUE_DIR / f'tmp_value_p{i+1}.txt', encoding='ISO-8859-1') as tmp_value_file:
    #             for line in tmp_value_file:
    #                 parse_line = parse("{}:{},{},{}", line.strip())
    #                 if parse_line != None:
    #                     sig_file, sig_line, v_name, value = os.path.basename(parse_line[0]), parse_line[1], parse_line[2], parse_line[3]
    #                     SIG_DIR = VALUE_DIR / sig_file / sig_line
    #                     os.makedirs(SIG_DIR, exist_ok=True)
    #                     with open(SIG_DIR / f'value_p{i+1}.txt', 'a') as value_file:
    #                         value_file.write(f'{v_name},{value}\n')




    

def read_signal_file(signal_file):
    result = []
    for line in signal_file:
        parse_line = parse("{}:{}\t{} {} {}", line.strip())
        if parse_line != None:
            result.append((os.path.basename(parse_line[0]), parse_line[1]))
    return result



def main():
    num_cores = multiprocessing.cpu_count()
    work_list = []
    for project in os.listdir(COVERAGE_DIR):
        for case in os.listdir(os.path.join(COVERAGE_DIR, project)):
            signal_filename = os.path.join(COVERAGE_DIR, project, case, "bic", "sparrow-out", "result_signal_filter.txt")
            signal_neg_filename = os.path.join(COVERAGE_DIR, project, case, "bic", "sparrow-out", "result_signal_neg_filter.txt")
            # print(signal_filename)

            if not os.path.isfile(signal_filename) or not os.path.isfile(signal_neg_filename) or not os.path.getsize(signal_filename) > 2 or not os.path.getsize(signal_neg_filename) > 2:
                # print("asdffsa")
                continue
            
            signal_file = open(signal_filename)
            signal_neg_file = open(signal_neg_filename)

            signal_list = read_signal_file(signal_file)
            signal_neg_list = read_signal_file(signal_neg_file)

            signal_file.close()
            signal_neg_file.close()

            signal_list += signal_neg_list
            # for (sig_file, sig_line) in signal_list:
            #     print(sig_file, sig_line)

            # for sig_file in signal_list:
            #     for sig in signal_list[file]:
            #         # before, _ = sig
            #         sig_line, _, _ = sig
            #         if not os.path.exists(OUTPUT_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / file / str(line)):
            #             work_list.append((project, case, sig_file, sig_line))

            # for sig_file in signal_neg_list:
            #     for sig in signal_neg_list[file]:
            #         # before, _ = sig
            #         sig_line, _, _ = sig
            #         if not os.path.exists(OUTPUT_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / file / str(line)):
            #             work_list.append((project, case, sig_file, sig_line))
            # neg_num, pos_num = get_test_num(project, case)
            # for i in range(pos_num):
            work_list.append((project, case, signal_list))


    # parmap.map(extract_one_signal, work_list, pm_pbar=True, pm_processes=10)
    
    num_process = 15
    split_work_list=[work_list[y-num_process:y] for y in range(num_process, len(work_list)+num_process,num_process)]
    for wl in tqdm(split_work_list):
        run_info = list(map(lambda x: (x[1][0], x[1][1], x[1][2], x[0]), enumerate(wl)))
        parmap.map(extract_one_signal, run_info, pm_pbar=True, pm_processes=num_process)


if __name__ == '__main__':
    main()