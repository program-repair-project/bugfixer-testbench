#!/bin/bash

MANYBUG_HASH=faf5f3ebaec45205cdf6a3db5be83f0055331aa4

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
	./tiff2pdf.sh
	result=$?
	if [[ $result != 0 ]]; then
        	cd .. && continue
	fi
	break
done

git checkout $current
