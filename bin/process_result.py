#!/usr/bin/env python3

import os
import argparse
from benchmark import benchmark, bic_location

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def open_result(project, case, timestamp, result_file):
    result_path = os.path.join(PROJECT_HOME, 'output', project, case, 'bic',
                               'sparrow-out', 'interval',
                               'merged-bnet-' + timestamp, result_file)
    result_file = open(result_path, 'r')
    return result_file


def get_rank_list(project, case, timestamp, result_file):
    file = open_result(project, case, timestamp, result_file)

    rank_list = []
    for line in file.read().splitlines()[1:]:
        rank, score, ground = line.split('\t')[:3]
        rank = int(rank)
        score = float(score)
        rank_list.append((rank, score, ground))
    file.close()
    return rank_list


def get_answer_index(rank_list):
    for rank, score, ground in rank_list:
        if 'TrueGround' in ground:
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
    return int((start+end)/2), end - start + 1, len(rank)


def get_one_result(project, case, timestamp, result_file):
    try:
        rank_list = get_rank_list(project, case, timestamp, result_file)
        answer_score, answer_index = get_answer_index(rank_list)
        start, end = get_same_rank(rank_list, answer_score)
        rank, tie, total = calculate_info(rank_list, start, end)
        return rank, tie, total
    except FileNotFoundError:
        return 0, 0, 0


def get_result(args, result_file):
    result = {}

    project, case, timestamp = args.project, args.case, args.timestamp

    if project:
        if case:
            result[project] = {
                case: get_one_result(project, case, timestamp, result_file)
            }
        else:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, timestamp,
                                                    result_file)
            result[project] = temp_project
    else:
        for project in benchmark:
            temp_project = {}
            for case in benchmark[project]:
                temp_project[case] = get_one_result(project, case, timestamp,
                                                    result_file)
            result[project] = temp_project
    return result


def print_result(result_list):
    #print(result)
    new_result = {}
    print(
        "Case\tInit_Rank\tInit_Tie\tInit_Total\tScore_Rank\tScore_Tie\tScore_Total"
    )
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
            print(case + "\t" + "\t".join(new_result[project][case]))


def main():

    parser = argparse.ArgumentParser(
        description='Get result data of project-case')
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('-t', '--timestamp', required=True, type=str)
    args = parser.parse_args()
    result_init = get_result(args, 'init.txt')
    result_score = get_result(args, 'score.txt')
    print_result([result_init, result_score])


if __name__ == '__main__':
    main()
