#!/bin/bash

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"

benchmark_array=("gmp" "libtiff" "php" "grep" "readelf" "shntool" "sed" "tar")
engine_array=("none" "tarantula" "ochiai" "dstar" "unival")
eps_array=("0.01" "0.05" "0.1")
default_rule_prob2_array=("0.45" "0.5" "0.55")

RESULT_FILE="$PROJECT_HOME"/result-of-run-all.txt

for engine in "${engine_array[@]}"; do
    echo "Engine: $engine" >>"$RESULT_FILE"
    for benchmark in "${benchmark_array[@]}"; do
        if [ "$engine" = "unival" ]; then
            if [ "$benchmark" = "gmp" ]; then
                timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -c 13420-13421 -e "$engine" -g --prune_cons)
                {
                    echo "Timestamp: $timestamp"
                    "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp"
                    echo ""
                } >>"$RESULT_FILE"
                pkill bingo
                continue
            elif [ "$benchmark" = "php" ] || [ "$benchmark" = "grep" ] || [ "$benchmark" = "readelf" ] || [ "$benchmark" = "sed" ] || [ "$benchmark" = "tar" ]; then
                continue
            fi
        elif [ "$engine" = "ochiai" ]; then
            for eps in "${eps_array[@]}"; do
                for drp2 in "${default_rule_prob2_array[@]}"; do
                    timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -e "$engine" -g --prune_cons --eps "$eps" --default_rule_prob2 "$drp2")
                    {
                        echo "Option: --eps $eps --default_rule_prob $drp2"
                        echo "Timestamp: $timestamp"
                        "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp"
                        echo ""
                    } >>"$RESULT_FILE"
                    pkill bingo
                done
            done
        else
            timestamp=$("$PROJECT_HOME"/bin/run-blazer.py -p "$benchmark" -e "$engine" -g --prune_cons)
            {
                echo "Timestamp: $timestamp"
                "$PROJECT_HOME"/bin/process_result.py -p "$benchmark" -t "$timestamp"
                echo ""
            } >>"$RESULT_FILE"
            pkill bingo
        fi
    done
done
