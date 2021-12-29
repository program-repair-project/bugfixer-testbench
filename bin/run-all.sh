#!/bin/bash

PROJECT_HOME="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
array=("0.99" "0.5" "0.01")

for rule_prob in "${array[@]}"; do
  for eps in "${array[@]}"; do
    for obs_prob in "${array[@]}"; do
      echo "$PROJECT_HOME/bin/run-blazer.py -p libtiff --default_rule_prob2 $rule_prob --eps $eps --default_obs_prob $obs_prob --debug --timestamp 20211229-00:00:00-$rule_prob-$eps-$obs_prob"
      $PROJECT_HOME/bin/run-blazer.py -p libtiff --default_rule_prob2 $rule_prob --eps $eps --default_obs_prob $obs_prob --debug --timestamp 20211229-00:00:00-$rule_prob-$eps-$obs_prob
    done
  done
done
