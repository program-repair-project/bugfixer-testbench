#!/usr/bin/env python3

import os
import argparse
from benchmark import benchmark, bic_location


PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def open_result(project, case, timestamp):
  result_path = os.path.join(PROJECT_HOME, 'output', project, case, 'bic', 'sparrow-out', 'interval', 'merged-bnet-' + timestamp, 'score.txt')
  result_file = open(result_path, 'r')
  return result_file


def get_rank_list(project, case, timestamp):
  file = open_result(project, case, timestamp)

  rank = []
  for line in file.read().splitlines()[1:]:
    cand = line.split('\t')[-1]
    score = float(line.split('\t')[1])
    rank.append((cand, score))
  return rank


def get_answer_index(project, case, rank):
  diff = 1 # design choice

  bic_location_list = bic_location[project][case]

  answer_list = [(file, t+line) for t in list(range(-diff, diff+1)) for (file, line) in bic_location_list]
  for i, (cand, score) in enumerate(rank):
    if (cand.split(':')[0], int(cand.split(':')[1])) in answer_list:
      return score, i
  return -1, -1


def get_same_rank(rank, answer_score):
  start = -1

  for i, (cand, score) in enumerate(rank):
    if score == answer_score:
      if start < 0:
        start = i
    elif score > answer_score:
      return start, i-1
  return start, i


def calculate_info(rank, start, end):
  return end, end-start+1, len(rank)


def get_one_result(project, case, timestamp):
  rank_list = get_rank_list(project, case, timestamp)
  answer_score, answer_index = get_answer_index(project, case, rank_list)
  start, end = get_same_rank(rank_list, answer_score)
  rank, tie, total = calculate_info(rank_list, start, end)
  return rank, tie, total


def get_result(args):
  result = {}

  project, case, timestamp = args.project, args.case, args.timestamp
  
  if project:
      if case:
          result[project] = {case: get_one_result(project, case, timestamp)}
      else:
          temp_project = {}
          for case in benchmark[project]:
              temp_project[case] = get_one_result(project, case, timestamp)
          result[project] = temp_project
  else:
      for project in benchmark:
          temp_project = {}
          for case in benchmark[project]:
              temp_project[case] = get_one_result(project, case, timestamp)
          result[project]=temp_project
  return result


def print_result(result):
    print(result)
    print("Rank\tTie\tTotal")
    for project in result:
        for case in result[project]:
            print("\t".join(map(str, result[project][case])))


def main():

  parser = argparse.ArgumentParser(
      description='Get result data of project-case')
  parser.add_argument('-p', '--project', type=str)
  parser.add_argument('-c', '--case', type=str)
  parser.add_argument('-t', '--timestamp', required=True, type=str)
  args = parser.parse_args()
  result = get_result(args)
  print_result(result)

if __name__ == '__main__':
  main()

