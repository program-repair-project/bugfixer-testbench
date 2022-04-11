#!/bin/bash
cd /experiment

rm -rf src
cp -rf parent src

cd /experiment/bic
./configure
cd /experiment/src
./configure
cd /experiment

./line_matching.py "./src/" "./bic/"
