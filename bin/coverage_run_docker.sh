#!/bin/bash

case_list=(
"2005-12-14-6746b87-0d3d51d"
"2005-12-21-3b848a7-3edb9cd"
"2006-02-23-b2ce5d8-207c78a"
"2006-03-03-a72cf60-0a36d7f"
"2007-08-24-827b6bc-22da1d6"
"2007-11-02-371336d-865f7b2"
"2008-12-30-362dee5-565eaa2"
"2009-02-05-764dbba-2e42d63"
"2009-06-30-b44af47-e0b51f3"
"2010-11-27-eb326f9-eec7ec0"
"2010-12-13-96a5fb4-bdba15c"
)

cd ..

for case in ${case_list[@]}; do
  ./bin/run-docker-differential.py libtiff-$case --rm
  echo $case
done
