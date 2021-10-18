#!/bin/bash

MANYBUG_HASH=21cfbd887b092a8ba00bb055625bc52b7fd3f7d7

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
	./tiffcrop-extract-logluv-3c-16b.sh 2>&1 | grep "Cannot compute"
	result39=$?
	if [[ $result39 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-minisblack-1c-16b.sh 2>&1 | grep "Cannot compute"
	result40=$?
	if [[ $result40 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-minisblack-1c-8b.sh 2>&1 | grep "Cannot compute"
	result41=$?
	if [[ $result41 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-miniswhite-1c-1b.sh 2>&1 | grep "Cannot compute"
	result43=$?
	if [[ $result43 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-palette-1c-1b.sh 2>&1 | grep "Cannot compute"
	result44=$?
	if [[ $result44 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-palette-1c-4b.sh 2>&1 | grep "Cannot compute"
	result45=$?
	if [[ $result45 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-palette-1c-8b.sh 2>&1 | grep "Cannot compute"
	result46=$?
	if [[ $result46 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-rgb-3c-16b.sh 2>&1 | grep "Cannot compute"
	result47=$?
	if [[ $result47 == 0 ]]; then
        	cd .. && continue
	fi

	./tiffcrop-extract-rgb-3c-8b.sh 2>&1 | grep "Cannot compute"
	result48=$?
	if [[ $result48 == 0 ]]; then
        	cd .. && continue
	fi
	break
done

git checkout $current
