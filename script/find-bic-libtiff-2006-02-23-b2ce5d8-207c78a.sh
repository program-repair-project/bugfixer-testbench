#!/bin/bash

MANYBUG_HASH=3cdfaeafb15963ad415b8ee34ecce79a9e0121d1

cd /experiment
git clone https://gitlab.com/libtiff/libtiff.git
cd libtiff
git checkout $MANYBUG_HASH
./configure
cp -rf /experiment/test mytest

while true; do
        current=`git log -n1 --pretty=format:"%H"`
        parent=`git log -n1 --pretty=format:"%P"`
        echo $parent
        git checkout $parent
        make -j
        if [[ $? != 0 ]]; then
                make clean
                continue
        fi
        cd /experiment/libtiff/mytest && make clean && make short_tag.log 2>&1 | grep "FAIL"
        result=$?
        if [[ $result == 0 ]]; then
                cd .. && continue
        else
                break
        fi
done

git checkout $current
