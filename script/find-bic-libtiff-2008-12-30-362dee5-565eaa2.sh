#!/bin/bash

MANYBUG_HASH=3cb55ee486adc98b0b7d556e1b4e70294e6d698e

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
        cd /experiment/libtiff/mytest
	./tiffcrop-extractz14-logluv-3c-16b.sh
	result=$?
	if [[ $result == 1 ]]; then
        	cd .. && continue
	fi
	./tiffcrop-extractz14-logluv-3c-16b.sh 2>&1 | grep "Cannot handle"
	result=$?
	if [[ $result == 0 ]]; then
        	cd .. && continue
	fi
	break
done

git checkout $current
