#!/bin/bash

MANYBUG_HASH=c1f6d214248e46b73120ade1d9188275e7afbe4c

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
       	cd /experiment/libtiff/mytest && make clean && make long_tag.log 2>&1 | grep "FAIL"
	result=$?
        if [[ $result == 0 ]]; then
                cd .. && continue
	else
		break
	fi
done

git checkout $current
