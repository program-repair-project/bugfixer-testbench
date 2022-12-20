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
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                            'sparrow-out', 'value', 'tiffcp.c', '704', assert_file) # 2005-12-21
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                            'sparrow-out', 'value', 'tiffcrop.c', '2649', assert_file) # 2010-12-13
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tiffcrop.c', '4536', assert_file) # 2009-02-05
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tif_dirwrite.c', '495', assert_file) # 2007-07-13
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tif_dirwrite.c', '188', assert_file) # 2006-02-23
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tif_dirwrite.c', '363', assert_file) # 2009-08-28
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tif_dirwrite.c', '495', assert_file) # 2007-07-13
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'tif_dirwrite.c', '483', assert_file) # 2010-11-27
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'inflate.c', '568', assert_file) # gzip 2009-08-16
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'inflate.c', '331', assert_file) # gzip 2009-09-26
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'gzip.c', '813', assert_file) # gzip 2009-10-19
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'util.c', '120', assert_file) # gzip 2010-01-30
    # assert_path = os.path.join(PROJECT_HOME, 'blazer_all_output', project, case, 'bic',
    #                             'sparrow-out', 'value', 'trees.c', '729', assert_file) # gzip 2010-02-19
    # assert_file = open(assert_path, 'r')
    assert_file = None
    default_path = os.path.join(OUTPUT_DIR, project, case, 'bic',
                               'sparrow-out', 'result_ochiai.txt.test')
    default_file = open(default_path, 'r')
    # print(result_file)
    return result_file, assert_file, default_file


def get_rank_list(project, case, inject_file, inject_line, result_file, assert_file):
    global pos_keep_rate
    global last_pos_rate
    result_file, assert_file, default_file = open_result(project, case, inject_file, inject_line, result_file, assert_file)
    neg_num , pos_num = get_test_num(project, case)

    rank_list = []
    default_neg_cov = {}
    assert_neg_cov = {}
    neg_nonzero = 0
    # for i, line in enumerate(assert_file):
    #     split_line = parse("{}:{}\t{} {} {} {}", line.strip())
    #     file, line, neg = split_line[0], int(split_line[1]), float(split_line[2])
    #     assert_neg_cov[(file, line)] = neg
    #     if neg > 0 :
    #         neg_nonzero += 1
    for i, line in enumerate(default_file):
        split_line = parse("{}:{}\t{} {} {} {}", line.strip())
        file, line, neg = os.path.basename(split_line[0]), int(split_line[1]), float(split_line[2])
        default_neg_cov[(file, line)] = neg
    print(neg_nonzero)
    total_num = 0
    weird_num = 0
    # print(assert_neg_cov[("tif_error.c", 60)])
    for i, line in enumerate(result_file):
        split_line = parse("{}:{}\t{} {} {} {}", line.strip())
        rank, score, ground = i + 1, float(split_line[-2]), (os.path.basename(split_line[0]), int(split_line[1]))
        

        nef = default_neg_cov[ground] if ground in default_neg_cov else 0

        nep = float(split_line[3])
        if ground == (inject_file, int(inject_line)):
            print(f"pos keep rate: {(pos_num-nep+float(split_line[-1]))/pos_num*100}")
            pos_keep_rate += (pos_num-nep+float(split_line[-1]))/pos_num*100
            last_pos_rate = (pos_num-nep+float(split_line[-1]))/pos_num*100
        if nef == 0 and nep == 0:
            weird_num += 1
            continue
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
        
    rank_list = [(j+1, x[0], x[1]) for j, x in enumerate(rank_list)]
    rank_dict = {}

    for rank, score, ground in rank_list:
        rank_dict[ground]=(rank, score)

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


def get_one_result(project, case, file, line, result_file, assert_file):
    try:
        rank_list = get_rank_list(project, case, file, line, result_file, assert_file)
        answer_score, answer_index = get_answer_index(project, case, rank_list)
        print(answer_score, answer_index)
        start, end = get_same_rank(rank_list, answer_score)
        rank, tie, total = calculate_info(rank_list, start, end)
        return rank, tie, total
    except FileNotFoundError:
        return 0, 0, 0


def get_result(project, case, file, line, result_file, assert_file):
    result = {}

    if project:
        if case:
            result[project] = {
                case: get_one_result(project, case, file, line, result_file, assert_file)
            }
        else:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, file, line, result_file, assert_file)
            result[project] = temp_project
    else:
        for project in benchmark:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, file, line, result_file, assert_file)
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
            rank_criteria = int(blazer_sheet.acell(f'F{sheet_row}').value)
            rate_100 = []
            rate_90 = []
            rate_80 = []
            for inject_file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                if inject_file in ['tmp', 'tmp2']:
                    continue
                if inject_file.startswith('tmp_value_'):
                        continue
                for inject_line in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file):
                    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "result_ochiai_assume.txt"):
                        result = get_result(project, case, inject_file, inject_line, 'result_ochiai_assume.txt', 'result_ochiai_assert.txt')
                        # print(result)
                        print(inject_file, inject_line)
                        print_result([result])
                        num += 1
                        sum_value += result[project][case][0]
                        if result[project][case][0] < min_value and result[project][case][0] > 0:
                            min_value = result[project][case][0]
                        if result[project][case][0] < rank_criteria and result[project][case][0] > 0:
                            below_num += 1
                            below_sum += result[project][case][0]
                        if last_pos_rate == 100 and result[project][case][0] > 0:
                            rate_100.append(result[project][case][0])
                        if last_pos_rate >= 90 and result[project][case][0] > 0:
                            rate_90.append(result[project][case][0])
                        if last_pos_rate >= 80 and result[project][case][0] > 0:
                            rate_80.append(result[project][case][0])


            print(f"num: {num}")
            print(f"min: {min_value}")         
            print(f"avg: {sum_value/num if num != 0 else 0}")
            print(f"below_num: {below_num}")
            print(f"below_avg: {0 if below_num == 0 else below_sum/below_num}")
            print(f"pos_keep_rate: {pos_keep_rate/num if num != 0 else 0}")
            # print(rate_100)
            # print(rate_90)
            # print(rate_80)
            rate_100_filter = list(filter(lambda x: x < rank_criteria, rate_100))
            rate_90_filter = list(filter(lambda x: x < rank_criteria, rate_90))
            rate_80_filter = list(filter(lambda x: x < rank_criteria, rate_80))
            print(f"rate_100 num, better_num, avg, better_avg, min: {len(rate_100)}, {len(rate_100_filter)}, {roundTraditional(0 if len(rate_100)==0 else sum(rate_100)/len(rate_100), 1)}, {roundTraditional(0 if len(rate_100_filter) == 0 else sum(rate_100_filter)/len(rate_100_filter), 1)}, {0 if len(rate_100) == 0 else min(rate_100)}")
            # blazer_sheet.update(f'O{sheet_row}', len(rate_100))
            # blazer_sheet.update(f'P{sheet_row}', len(rate_100_filter))
            # blazer_sheet.update(f'Q{sheet_row}', roundTraditional(0 if len(rate_100)==0 else sum(rate_100)/len(rate_100), 1))
            # blazer_sheet.update(f'R{sheet_row}', roundTraditional(0 if len(rate_100_filter) == 0 else sum(rate_100_filter)/len(rate_100_filter), 1))
            # blazer_sheet.update(f'S{sheet_row}', min(rate_100))
            # blazer_sheet.update(f'P{sheet_row}:T{sheet_row}', [[len(rate_100), len(rate_100_filter), roundTraditional(0 if len(rate_100)==0 else sum(rate_100)/len(rate_100), 1), roundTraditional(0 if len(rate_100_filter) == 0 else sum(rate_100_filter)/len(rate_100_filter), 1), 0 if len(rate_100) == 0 else min(rate_100)]])
            print(f"rate_90 num, better_num, avg, better_avg, min: {len(rate_90)}, {len(rate_90_filter)}, {roundTraditional(0 if len(rate_90)==0 else sum(rate_90)/len(rate_90), 1)}, {roundTraditional(0 if len(rate_90_filter) == 0 else sum(rate_90_filter)/len(rate_90_filter), 1)}, {0 if len(rate_90) == 0 else min(rate_90)}")
            # blazer_sheet.update(f'T{sheet_row}', len(rate_90))
            # blazer_sheet.update(f'U{sheet_row}', len(rate_90_filter))
            # blazer_sheet.update(f'V{sheet_row}', roundTraditional(0 if len(rate_90)==0 else sum(rate_90)/len(rate_90), 1))
            # blazer_sheet.update(f'W{sheet_row}', roundTraditional(0 if len(rate_90_filter) == 0 else sum(rate_90_filter)/len(rate_90_filter), 1))
            # blazer_sheet.update(f'X{sheet_row}', min(rate_90))
            # blazer_sheet.update(f'U{sheet_row}:Y{sheet_row}', [[len(rate_90), len(rate_90_filter), roundTraditional(0 if len(rate_90)==0 else sum(rate_90)/len(rate_90), 1), roundTraditional(0 if len(rate_90_filter) == 0 else sum(rate_90_filter)/len(rate_90_filter), 1), 0 if len(rate_90) == 0 else min(rate_90)]])
            print(f"rate_80 num, better_num, avg, better_avg, min: {len(rate_80)}, {len(rate_80_filter)}, {roundTraditional(0 if len(rate_80)==0 else sum(rate_80)/len(rate_80), 1)}, {roundTraditional(0 if len(rate_80_filter) == 0 else sum(rate_80_filter)/len(rate_80_filter), 1)}, {0 if len(rate_80) == 0 else min(rate_80)}")
            # blazer_sheet.update(f'Y{sheet_row}', len(rate_80))
            # blazer_sheet.update(f'Z{sheet_row}', len(rate_80_filter))
            # blazer_sheet.update(f'AA{sheet_row}', roundTraditional(0 if len(rate_80)==0 else sum(rate_80)/len(rate_80), 1))
            # blazer_sheet.update(f'AB{sheet_row}', roundTraditional(0 if len(rate_80_filter) == 0 else sum(rate_80_filter)/len(rate_80_filter), 1))
            # blazer_sheet.update(f'AC{sheet_row}', min(rate_80))
            # blazer_sheet.update(f'Z{sheet_row}:AD{sheet_row}', [[len(rate_80), len(rate_80_filter), roundTraditional(0 if len(rate_80)==0 else sum(rate_80)/len(rate_80), 1), roundTraditional(0 if len(rate_80_filter) == 0 else sum(rate_80_filter)/len(rate_80_filter), 1), 0 if len(rate_80) == 0 else min(rate_80)]])
            # sleep(5)


if __name__ == '__main__':
    main()
