#!/bin/bash

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../ && pwd)"
SPARROW_HOME=$PROJECT_HOME/sparrow

if [[ $1 == "clean" ]]; then
  echo "clean"
  rm -rf parent/sparrow-out
  rm -rf bic/sparrow-out
  exit 0
fi

pushd parent
$SPARROW_HOME/bin/sparrow -extract_datalog_fact_full_no_opt_dag abs.c >& /dev/null
popd && pushd bic
$SPARROW_HOME/bin/sparrow -extract_datalog_fact_full_no_opt_dag abs.c >& /dev/null
popd

cp coverage.txt line-matching.json bic/sparrow-out/

$PROJECT_HOME/bingo/bin/blazer -default_edb_prob 0.5 -parent_dir parent/sparrow-out bic/sparrow-out
