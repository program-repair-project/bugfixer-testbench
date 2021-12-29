#!/bin/bash
cd /experiment/bic
BIC_REV=$( hg parent | grep changeset | grep -Po ' \d*:' | grep -Po '\d*' )
hg update -C -r $BIC_REV
cd /experiment
cp -rf src/tests .
rm -rf src
cp -rf bic src
cd /experiment/src
PARENT_REV=$(($BIC_REV-1))
hg update -C -r $PARENT_REV
cd /experiment/bic
./configure
cd /experiment/src
./configure
cd /experiment
./line_matching.py "./src/" "./bic/"
cd /experiment/src
rm -rf tests
cp -rf ../tests .
cd /experiment
