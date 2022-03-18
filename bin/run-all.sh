#!/bin/bash

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

engine_array=("none" "ochiai" "tarantula" "dstar" "unival")
eps_array=("0.005" "0.01" "0.05" "0.1")
default_rule_prob2_array=("0.4" "0.45" "0.5" "0.55")

RESULT_FILE="$PROJECT_HOME"/result-of-run-all.txt

for engine in "${engine_array[@]}"; do
    echo "Engine: $engine" >>"$RESULT_FILE"
    if [ "$engine" = "unival" ]; then
        timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p gmp -c 13420-13421 -e "$engine" -g --prune_cons)
        {
            echo "Timestamp: $timestamp"
            "$PROJECT_HOME"/bin/process_result.py -p gmp -t "$timestamp"
            echo ""
        } >>"$RESULT_FILE"
        pkill bingo
        timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p libtiff -e "$engine" -g --prune_cons)
        {
            echo "Timestamp: $timestamp"
            "$PROJECT_HOME"/bin/process_result.py -p libtiff -t "$timestamp"
            echo ""
        } >>"$RESULT_FILE"
        pkill bingo
        timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p shntool -e "$engine" -g --prune_cons)
        {
            echo "Timestamp: $timestamp"
            "$PROJECT_HOME"/bin/process_result.py -p shntool -t "$timestamp"
            echo ""
        } >>"$RESULT_FILE"
        pkill bingo
    elif [ "$engine" = "ochiai" ]; then
        for eps in "${eps_array[@]}"; do
            timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -e "$engine" -g --prune_cons --eps "$eps" --default_rule_prob 0.4)
            {
                echo "Option: --eps $eps --default_rule_prob2 0.40"
                echo "Timestamp: $timestamp"
                "$PROJECT_HOME"/bin/process_result.py -t "$timestamp"
                echo ""
            } >>"$RESULT_FILE"
            pkill bingo
        done
        for drp2 in "${default_rule_prob2_array[@]}"; do
            timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -e "$engine" -g --prune_cons --eps 0.005 --default_rule_prob2 "$drp2")
            {
                echo "Option: --eps 0.005 --default_rule_prob2 $drp2"
                echo "Timestamp: $timestamp"
                "$PROJECT_HOME"/bin/process_result.py -t "$timestamp"
                echo ""
            } >>"$RESULT_FILE"
            pkill bingo
        done
    fi
    timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -e "$engine" -g --prune_cons)
    {
        echo "Timestamp: $timestamp"
        "$PROJECT_HOME"/bin/process_result.py -t "$timestamp"
        echo ""
    } >>"$RESULT_FILE"
    pkill bingo
done
