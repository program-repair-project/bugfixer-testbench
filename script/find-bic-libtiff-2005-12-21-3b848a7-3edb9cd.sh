#!/bin/bash

MANYBUG_HASH=f5ebfca20231dfc9b6be2536a195d5d18b2cf3cd

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
        make -j || continue
        cd mytest && ./tiffcp-split.sh 2>&1 | grep "Warning"
        if [[ $? == 0 ]]; then
                cd .. && continue
        fi

        ./tiffcp-split.sh
        if [[ $? == 0 ]]; then
                break
        else
                cd .. && continue
        fi
done

git checkout $current
