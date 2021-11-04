#!/bin/bash

cd /experiment/src

while true; do
        current=`git log -n1 --pretty=format:"%H"`
        parent=`git log -n1 --pretty=format:"%P"`
        echo $parent
        git checkout $parent
        make clean && make -j || continue
        sapi/cli/php ext/phar/tests/bug60164.phpt | grep "Fatal error: Uncaught exception 'UnexpectedValueException' with message 'internal corruption of phar"
        if [[ $? == 0 ]]; then
                continue
        fi

        break
done

git checkout $current
