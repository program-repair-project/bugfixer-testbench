#!/bin/bash

PROJECT_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd ../ && pwd)"
SPARROW_HOME=$PROJECT_HOME/sparrow

pushd parent
$SPARROW_HOME/bin/sparrow -extract_datalog_fact_full_no_opt abs.c >& /dev/null
popd && pushd bic
$SPARROW_HOME/bin/sparrow -extract_datalog_fact_full_no_opt abs.c >& /dev/null
popd

cp coverage.txt line-matching.json bic/sparrow-out/

$PROJECT_HOME/bingo/bin/blazer -default_prob 0.5 -parent_dir parent/sparrow-out bic/sparrow-out
