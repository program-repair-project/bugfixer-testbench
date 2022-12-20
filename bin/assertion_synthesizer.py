#!/usr/bin/env python3

from z3 import *
from parse import *
import os
import json
from pathlib import Path

PROJECT_HOME = Path(__file__).resolve().parent.parent
DATA_DIR = Path('/data/jongchan/')
COVERAGE_DIR = DATA_DIR / 'blazer_all_output'
OUTPUT_DIR = DATA_DIR / 'blazer_all_output'


def parse_result_file(result_file):
    result = dict()
    for i, line in enumerate(result_file):
        parse_line = parse("{},{}", line.strip())
        varname, value = parse_line[0], parse_line[1]
        if varname not in result:
            result[varname]=[]
        # if "NA:" not in value and "null" not in value:
        if value not in result[varname] and (value.isdigit() or (value.startswith('-') and value[1:].isdigit())):
            # if varname in result and result[varname] != value:
            #     raise Exception("value is different")
            result[varname].append(value)
        elif (len(value)==1 and value.isascii()) and str(ord(value)) not in result[varname]:
            result[varname].append(str(ord(value)))
    return result


def make_z3var_map(value_map):
    z3var_map = dict()

    for tc in value_map['neg']:
        for varname in value_map['neg'][tc]:
            if varname not in z3var_map:
                z3var_map[varname] = Int(varname)
    for tc in value_map['pos']:
        for varname in value_map['pos'][tc]:
            if varname not in z3var_map:
                z3var_map[varname] = Int(varname)
    return z3var_map

def check_assert_sat(value_map, z3var_map):
    neg_cond = True
    pos_cond = False

    if len(value_map['neg']) == 0:
        return False

    for tc in value_map['neg']:
        tc_cond = True
        for varname in value_map['neg'][tc]:
            var_cond = False
            for value in value_map['neg'][tc][varname]:
                tmp = z3var_map[varname] == int(value)
                var_cond = Or(tmp, var_cond)
            tc_cond = And(var_cond, tc_cond)
        neg_cond = And(Not(tc_cond), neg_cond)

    # for tc in value_map['pos']:
    #     tc_cond = True
    #     for varname in value_map['pos'][tc]:
    #         # print("problem:", varname, value_map['pos'][tc][varname])
    #         tc_cond = And(z3var_map[varname]==int(value_map['pos'][tc][varname]), tc_cond)
    #     pos_cond = Or(tc_cond, pos_cond)
    for tc in value_map['pos']:
        tc_cond = True
        for varname in value_map['pos'][tc]:
            var_cond = False
            for value in value_map['pos'][tc][varname]:
                tmp = z3var_map[varname] == int(value)
                var_cond = Or(tmp, var_cond)
            tc_cond = And(var_cond, tc_cond)
        assert_solver = Solver()
        assert_solver.add(And(neg_cond, tc_cond))
        if unsat == assert_solver.check():
            break
    else:
        return True
    # print(assert_solver.model())
    return False



def main():
    for project in os.listdir(COVERAGE_DIR):
        for case in os.listdir(COVERAGE_DIR / project):
            if not os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                continue
            for inject_file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value'):
                if inject_file in ['tmp', 'tmp2']:
                    continue
                if inject_file.startswith('tmp_value_'):
                    continue
                for inject_line in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file):
                    # if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt"):
                    #     continue
                    if os.path.exists(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt"):
                        continue
                    print(project, case, inject_file, inject_line)
                    value_map = dict()
                    value_map['neg']=dict()
                    value_map['pos']=dict()
                    for file in os.listdir(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line):
                        if not file.startswith("value"):
                            continue
                        if os.path.splitext(file)[0].split('_')[-1].startswith('p'):
                            continue
                        # print("value_map", value_map)
                        with open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / file) as value_file:
                            try:
                                if os.path.splitext(file)[0].split('_')[-1].startswith('n'):
                                    value_map['neg'][os.path.splitext(file)[0].split('_')[-1]] = parse_result_file(value_file)
                                # else:
                                #     value_map['pos'][os.path.splitext(file)[0].split('_')[-1]] = parse_result_file(value_file)
                            except:
                                break
                    else:
                        if True:
                            with open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt", 'w') as output_file:
                                output_file.write(json.dumps(value_map))
                        else:
                            with open(COVERAGE_DIR / project / case / 'bic' / 'sparrow-out' / 'value' / inject_file / inject_line / "assertion.txt", 'w') as output_file:
                                output_file.write(json.dumps({}))



if __name__ == '__main__':
    main()
