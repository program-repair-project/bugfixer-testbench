#!/bin/bash

cd /experiment/bic
git reset --hard HEAD
cd /experiment
rm -rf src
cp -rf bic src
cd /experiment/src
git reset --hard HEAD~1
cd /experiment
./line_matching.py "./bic/" "./src/"
cd /experiment/src
rm -rf test
cp -rf ../test .
cd /experiment
