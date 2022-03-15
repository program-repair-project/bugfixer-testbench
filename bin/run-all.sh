#!/bin/bash

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

benchmark_array=("gmp" "libtiff" "php" "grep" "readelf" "shntool" "sed" "tar")
engine_array=("tarantula" "ochiai" "jaccard" "unival")
eps_array=("0.005" "0.001" "0.05" "0.1")
default_rule_prob_array=("0.9" "0.8")

RESULT_FILE="$PROJECT_HOME"/result-of-run-all.txt

for engine in "${engine_array[@]}"; do
    echo "Engine: $engine" >>"$RESULT_FILE"
    for benchmark in "${benchmark_array[@]}"; do
        if [ "$engine" = "unival" ]; then
            if [ "$benchmark" = "gmp" ]; then
                timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -c 13420-13421 -e "$engine" -g --prune_cons)
                echo "Timestamp: $timestamp" >>"$RESULT_FILE"
                "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp" >>"$RESULT_FILE"
                continue
            elif [ "$benchmark" = "php" ] || [ "$benchmark" = "grep" ] || [ "$benchmark" = "readelf" ] || [ "$benchmark" = "sed" ] || [ "$benchmark" = "tar" ]; then
                continue
            fi
        fi
        timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -e "$engine" -g --prune_cons)
        echo "Timestamp: $timestamp" >>"$RESULT_FILE"
        "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp" >>"$RESULT_FILE"
        if [ "$engine" = "ochiai" ]; then
            for eps in "${eps_array[@]}"; do
                echo "Option: --eps $eps" >>"$RESULT_FILE"
                timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -e "$engine" -g --prune_cons --eps "$eps")
                echo "Timestamp: $timestamp" >>"$RESULT_FILE"
                "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp" >>"$RESULT_FILE"
            done
            for drp in "${default_rule_prob_array[@]}"; do
                echo "Option: --default_rule_prob $drp" >>"$RESULT_FILE"
                timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -e "$engine" -g --prune_cons --default_rule_prob "$drp")
                echo "Timestamp: $timestamp" >>"$RESULT_FILE"
                "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp" >>"$RESULT_FILE"
            done
        fi

    done
done
