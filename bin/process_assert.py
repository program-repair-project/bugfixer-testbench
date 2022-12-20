#!/usr/bin/env python3

import os
import argparse
from parse import *
from benchmark import benchmark, patch_location
from pathlib import Path
import math
import yaml
import gspread
from time import sleep


PROJECT_HOME = Path(__file__).resolve().parent.parent
DATA_DIR = Path('/data/jongchan/')
COVERAGE_DIR = DATA_DIR / 'blazer_all_output'
OUTPUT_DIR = DATA_DIR / 'blazer_all_output'
YML_DIR = PROJECT_HOME / 'benchmark'

pos_keep_rate = 0
last_pos_rate = 0
rate_100 = []
rate_90 = []
rate_80 = []


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


def open_result(project, case, file, line, result_file, assert_file):
    result_path = os.path.join(OUTPUT_DIR, project, case, 'bic',
                               'sparrow-out', 'value', file, line, result_file)
    result_file = open(result_path, 'r')
    # print(result_file)
    return result_file


def get_default_rank_list(project, case, result_file):
    result_path = os.path.join(OUTPUT_DIR, project, case, 'bic',
                               'sparrow-out',  result_file)
    result_file = open(result_path, 'r')
    default_cov = {}
    for i, line in enumerate(result_file):
        split_line = parse("{}:{}\t{} {} {} {}", line.strip())
        file, line, neg, pos = os.path.basename(split_line[0]), int(split_line[1]), float(split_line[2]), float(split_line[3])
        default_cov[(file, line)] = (neg, pos)
    # print(result_file)
    result_file.close()
    return default_cov

def get_rank_list(project, case, inject_file, inject_line, result_file, assert_file, default_cov):
    global pos_keep_rate
    global last_pos_rate
    result_file = open_result(project, case, inject_file, inject_line, result_file, assert_file)
    # default_file = open_default_result(project, case, "result_ochiai.txt")
    neg_num , pos_num = get_test_num(project, case)

    rank_list = []
    # default_pos_cov = {}
    neg_nonzero = 0
    total_num = 0
    weird_num = 0
    # print(assert_neg_cov[("tif_error.c", 60)])
    # for i, line in enumerate(default_file):
    #     split_line = parse("{}:{}\t{} {} {} {}", line.strip())
    #     file, line, neg, pos = os.path.basename(split_line[0]), int(split_line[1]), float(split_line[2]), float(split_line[3])
    #     default_pos_cov[(file, line)] = (neg, pos)

    for i, line in enumerate(result_file):
        split_line = parse("{}:{}\t{} {} {} {}", line.strip())
        rank, score, ground = i + 1, float(split_line[-2]), (os.path.basename(split_line[0]), int(split_line[1]))
        
        # _, nep = default_pos_cov[ground] if ground in default_pos_cov and default_pos_cov[ground][0] > 0 else (-1, -1)
        _, nep = default_cov[ground] if ground in default_cov else (-1, -1)
        if nep >= 0:
            nef = float(split_line[2])
            
            total_num += 1
            nnf = neg_num - nef
            denom1 = nef + nnf
            denom2 = nef + nep
            
            denom = math.sqrt(denom1 * denom2)

            score = nef / denom

            
            rank = int(rank)
            score = float(score)
            rank_list.append((score, ground))
    rank_list.sort(key=lambda x: -(x[0]))
        # rank_list.append((rank, score, ground))
        
    rank_list = [(j+1, x[0], x[1]) for j, x in enumerate(rank_list)]
    # rank_dict = {}

    # for rank, score, ground in rank_list:
    #     rank_dict[ground]=(rank, score)

    # for cand in default_neg_cov:
    #     if cand not in rank_dict and default_neg_cov[cand] > 0:
    #         rank_list.append((-1, 1.0, cand))
    rank_list.sort(key=lambda x: -(x[1]))
    rank_list = [(j+1, x[1], x[2]) for j, x in enumerate(rank_list)]


    result_file.close()
    # assert_file.close()
    # print(total_num, weird_num)
    return rank_list


def get_answer_index(project, case, rank_list):
    for rank, score, ground in rank_list:
        if ground in patch_location[project][case]:
            return score, rank
    return 2.0, -1


def get_same_rank(rank_list, answer_score):
    start = -1

    for rank, score, _ in rank_list:
        if score == answer_score:
            if start < 0:
                start = rank
        elif score < answer_score:
            return start, rank - 1
    #print(start, i)
    return start, len(rank_list)


def calculate_info(rank, start, end):
    return end, end - start + 1, len(rank)


def get_one_result(project, case, file, line, result_file, assert_file, default_cov):
    try:
        rank_list = get_rank_list(project, case, file, line, result_file, assert_file, default_cov)
        answer_score, answer_index = get_answer_index(project, case, rank_list)
        # print("answer:", answer_score, answer_index)
        start, end = get_same_rank(rank_list, answer_score)
        rank, tie, total = calculate_info(rank_list, start, end)
        return rank, tie, total
    except FileNotFoundError:
        return 0, 0, 0


def get_result(project, case, file, line, result_file, assert_file, default_cov):
    result = {}

    if project:
        if case:
            result[project] = {
                case: get_one_result(project, case, file, line, result_file, assert_file, default_cov)
            }
        else:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, file, line, result_file, assert_file, default_cov)
            result[project] = temp_project
    else:
        for project in benchmark:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, file, line, result_file, assert_file, default_cov)
            result[project] = temp_project
    return result


def print_result(result_list):
    #print(result)
    new_result = {}
    for result in result_list:
        for project in result:
            if project not in new_result:
                new_result[project] = {}
            for case in result[project]:
                if case not in new_result[project]:
                    new_result[project][case] = []
                new_result[project][case].append("\t".join(
                    map(str, result[project][case])))
    for project in new_result:
        for case in new_result[project]:
            print(project + "\t" + case + "\t" +
                  "\t".join(new_result[project][case]))


def roundTraditional(val, digits):
    return round(val+10**(-len(str(val))-1), digits)


def main():
    global rate_100, rate_90, rate_80
    gc = gspread.service_account(filename=str(PROJECT_HOME / 'bin' / "jongchan-googlekey.json"))
    parser = argparse.ArgumentParser(
        description='Get result data of project-case')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('-e', '--engine', type=str)
    args = parser.parse_args()

    blazer_sheet = gc.open("blazer").worksheet("자동화")
    case_list = blazer_sheet.col_values(2)

    print("Project\tCase\tRank\tTie\tTotal")
    for project in os.listdir(COVERAGE_DIR):
        for case in os.listdir(COVERAGE_DIR / project):
            if not os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                continue
            num = 0
            min_value = 10000000
            sum_value = 0
            below_num = 0
            below_sum = 0
            sheet_row = blazer_sheet.find(case).row
            # rank_criteria = int(blazer_sheet.acell(f'F{sheet_row}').value)
            min_signal = ("", 0)
            default_cov = get_default_rank_list(project, case, "result_ochiai.txt.test")
            for inject_file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                if inject_file in ['tmp', 'tmp2']:
                    continue
                if inject_file.startswith('tmp_value_'):
                    continue
                for inject_line in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file):
                    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "result_ochiai_assert.txt"):
                        # print(project, case, inject_file, inject_line)
                        result = get_result(project, case, inject_file, inject_line, 'result_ochiai_assert.txt', 'result_ochiai_assert.txt', default_cov)
                        # print(result)
                        print(inject_file, inject_line)
                        print_result([result])
                        num += 1
                        sum_value += result[project][case][0]
                        if result[project][case][0] < min_value and result[project][case][0] > 0:
                            min_value = result[project][case][0]
                            min_signal = (inject_file, inject_line)
                        # if result[project][case][0] < rank_criteria and result[project][case][0] > 0:
                        #     below_num += 1
                        #     below_sum += result[project][case][0]


            print(f"num: {num}")
            print(f"min: {min_value}")         
            print(f"avg: {sum_value/num if num != 0 else 0}")
            # print(f"below_num: {below_num}")
            # print(f"below_avg: {0 if below_num == 0 else below_sum/below_num}")
            print(f"pos_keep_rate: {pos_keep_rate/num if num != 0 else 0}")
            print("min_signal:", min_signal)
            # sleep(5)


if __name__ == '__main__':
    main()
