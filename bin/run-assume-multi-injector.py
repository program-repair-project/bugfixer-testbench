#!/usr/bin/env python3

from parse import *
import os
from pathlib import Path
import subprocess
from asyncio.subprocess import DEVNULL
import logging
import multiprocessing
import parmap
import yaml
import random
import numpy as np


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


def get_test_num(project, case):
    with open(os.path.join(YML_DIR, project, f'{project}.bugzoo.yml')) as f:
        bug_data = yaml.load(f, Loader=yaml.FullLoader)
        neg_num = 0
        pos_num = 0
        for data in bug_data['bugs']:
            # print(data)
            if data['name'].split(':')[-1] == case:
                neg_num = int(data['test-harness']['failing'])
                pos_num = int(data['test-harness']['passing'])
                # print('FIND!!')
                break
        else:
            raise Exception("TEST NUM NOT FOUND")
    return neg_num, pos_num


def inject_assume(run_info):
    project, case, signal_list = run_info
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
    
    exp_name = "-".join(list(map(lambda x: str(x[0][0]) + ('t' if x[1] else 'f'), signal_list)))
    

    print("[*] Injecting assume of : %s-%s-%s" % (project, case, exp_name))
    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'exp_name.txt'):
        exp_name_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'exp_name.txt', 'r')
        exp_name_list = exp_name_file.read().splitlines()
        exp_name_file.close()
        if exp_name in exp_name_list:
            return

    # run docker
    run_cmd_and_check([f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d', '--rm', '--name', f'{project}-{case}-{exp_name}-assume'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)

    docker_id = f'{project}-{case}-{exp_name}-assume'

    run_cmd_and_check(
            ['docker', 'exec', docker_id, 'bash', '-c', f'touch /experiment/signal_list.txt'])

    run_cmd_and_check(
            ['docker', 'exec', docker_id, 'bash', '-c', f'touch /experiment/signal_neg_list.txt'])

    for ((_, sig_file, sig_line), is_pos) in signal_list:
        # print(f'{project}-{case}-{exp_name}: ', signal_list, ['docker', 'exec', docker_id, 'bash', '-c', f"echo {sig_file}:{sig_list} >> /experiment/signal_list.txt"])
        if is_pos:
            run_cmd_and_check(
                ['docker', 'exec', docker_id, 'bash', '-c', f"echo {sig_file}:{sig_line} >> /experiment/signal_list.txt"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
        else:
            run_cmd_and_check(
                ['docker', 'exec', docker_id, 'bash', '-c', f"echo {sig_file}:{sig_line} >> /experiment/signal_neg_list.txt"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)

    run_cmd_and_check(
        ['docker', 'exec', docker_id, '/bugfixer/localizer/main.exe', '-engine', 'assume', '.'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    
    exp_name_index = 0
    while(exp_name_index == 0):
        exp_name_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'exp_name.txt', 'a')
        exp_name_file.write(f'{exp_name}\n')
        exp_name_file.close()
        exp_name_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'exp_name.txt', 'r')
        exp_name_index = exp_name_file.read().splitlines().index(exp_name) + 1
        exp_name_file.close()
        if(exp_name_index == 0):
            print("DATARACE OR SOMETHING")

    os.makedirs(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / f'{exp_name_index}', exist_ok=True)

    run_cmd_and_check(
        ['docker', 'cp', f'{docker_id}:/experiment/localizer-out/result_ochiai_assume.txt', f"{str(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / f'{exp_name_index}')}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
    
    run_cmd_and_check(['docker', 'kill', f'{docker_id}'],
                      stdout=subprocess.DEVNULL,
                      stderr=subprocess.DEVNULL)


def read_signal_file(signal_file):
    result = []
    for i, line in enumerate(signal_file):
        parse_line = parse("{}:{}\t{} {}", line.strip())
        if parse_line != None:
            result.append((i, parse_line[0], parse_line[1]))
    return result


def split_by_size(a, size):
    # return list(map(lambda x: np.array(x).flatten().tolist(), list(map(lambda x: x.tolist(), np.split(a, np.arange(size,len(a),size))))))
    tmp_list = [a[i:i+size] for i in range(0,len(a),size)]
    result = []
    for e in tmp_list:
        tmp = []
        for i in e:
            tmp += i
        result.append(tmp)
    return result


def main():
    num_cores = multiprocessing.cpu_count()
    # work_list = []
    for project in os.listdir(COVERAGE_DIR):
        for case in os.listdir(COVERAGE_DIR / project):
            if not os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                continue 
            
            _, pos_num = get_test_num(project, case)

            signal_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'result_signal_filter.txt')
            signal_list = read_signal_file(signal_file)
            signal_neg_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'result_signal_neg_filter.txt')
            signal_neg_list = read_signal_file(signal_neg_file)
            os.makedirs(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2', exist_ok=True)

            signal_list_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'signal_list.txt', 'w')
            signal_neg_list_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'signal_neg_list.txt', 'w')
            for (_, sig_file, sig_line) in signal_list:
                signal_list_file.write(f"{sig_file}:{sig_line}\n")
            for (_, sig_file, sig_line) in signal_neg_list:
                signal_neg_list_file.write(f"{sig_file}:{sig_line}\n")
            signal_list_file.close()
            signal_neg_list_file.close()


            # print(signal_list)

            # for inject_file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
            #     for inject_line in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file):
            #         if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "result_ochiai_assume.txt") and os.path.getsize(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "result_ochiai_assume.txt") > 2:
            #             continue
            #         work_list.append((project, case, inject_file, inject_line))
            rate_90_filter = []
            for (i, sig_file, sig_line) in signal_list:
                if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / sig_file / sig_line / 'result_ochiai_assume.txt'):
                    assume_result_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / sig_file / sig_line / 'result_ochiai_assume.txt')
                    assume_keep_rate = 0
                    for line in assume_result_file:
                        parse_line = parse("{}:{}\t{} {} {} {}", line.strip())
                        if parse_line != None and parse_line[0] == sig_file and parse_line[1] == sig_line:
                            assume_keep_rate = (pos_num - (float(parse_line[3]) - float(parse_line[5])))/pos_num*100
                            break
                    else:
                        continue
                    if assume_keep_rate >= 100:
                        rate_90_filter.append((i, True, sig_file, sig_line))
            
            rate_90_filter_neg = []
            for (i, sig_file, sig_line) in signal_neg_list:
                if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / sig_file / sig_line / 'result_ochiai_assume.txt'):
                    assume_result_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / sig_file / sig_line / 'result_ochiai_assume.txt')
                    assume_keep_rate = 0
                    for line in assume_result_file:
                        parse_line = parse("{}:{}\t{} {} {} {}", line.strip())
                        if parse_line != None and parse_line[0] == sig_file and parse_line[1] == sig_line:
                            assume_keep_rate = (pos_num - (float(parse_line[3]) - float(parse_line[5])))/pos_num*100
                            break
                    else:
                        continue
                    if assume_keep_rate >= 100:
                        rate_90_filter_neg.append((i, False, sig_file, sig_line))

            signal_index_list = list(map(lambda x: [(x[0], x[1])], (rate_90_filter + rate_90_filter_neg)))
            print(signal_index_list)
            while(len(signal_index_list) >= 2):
                work_list = []
                random.shuffle(signal_index_list)
                signal_index_list = split_by_size(signal_index_list, 2)
                print(signal_index_list)
                for e in signal_index_list:
                    work_list.append((project, case, list(map(lambda x: (signal_list[x[0]], x[1]) if x[1] else (signal_neg_list[x[0]], x[1]), e))))
                parmap.map(inject_assume, work_list, pm_pbar=True, pm_processes=(num_cores-1))
                assume_keep_rate = 100
                rate_90_filter = []
                for cand in signal_index_list:
                    assume_keep_rate = 1000
                    exp_name_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / 'exp_name.txt', 'r')
                    exp_name_list = exp_name_file.read().splitlines()
                    exp_name = "-".join(list(map(lambda x: str(x[0]) + ('t' if x[1] else 'f'), cand)))
                    exp_name_index = exp_name_list.index(exp_name) + 1
                    if not os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / f'{exp_name_index}' / 'result_ochiai_assume.txt'):
                        raise Exception("NO exp_name_index dir")
                        continue
                    cand_result_file = open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / 'tmp2' / f'{exp_name_index}' / 'result_ochiai_assume.txt')
                    for line in cand_result_file:
                        parse_line = parse("{}:{}\t{} {} {} {}", line.strip())
                        cand_file_list = list(map(lambda x: signal_list[x[0]][1] if x[1] else signal_neg_list[x[0]][1], cand))
                        cand_line_list = list(map(lambda x: signal_list[x[0]][2] if x[1] else signal_neg_list[x[0]][2], cand))
                        if parse_line != None and parse_line[0] in cand_file_list and parse_line[1] in cand_line_list:
                            if assume_keep_rate > (pos_num - (float(parse_line[3]) - float(parse_line[5])))/pos_num*100:
                                assume_keep_rate = (pos_num - (float(parse_line[3]) - float(parse_line[5])))/pos_num*100
                        # raise Exception(f"{project}-{case}-{exp_name}-Not found")
                    if 100 >= assume_keep_rate and assume_keep_rate >= 90:
                        rate_90_filter.append(cand)
                signal_index_list = rate_90_filter





    # parmap.map(inject_assume, work_list, pm_pbar=True, pm_processes=(num_cores-1))


if __name__ == '__main__':
    main()