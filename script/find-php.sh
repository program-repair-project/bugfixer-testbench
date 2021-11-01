#!/bin/bash

git config --global user.email "you@example.com"
git config --global user.name "Your Name"
cd /experiment/src
git stash

while true; do
        current=`git log -n1 --pretty=format:"%H"`
        parent=`git log -n1 --pretty=format:"%P"`
        echo $parent
        git stash
        git checkout $parent
        git stash pop
        make -j || continue
        ../test.sh n1
        if [[ $? == 1 ]]; then
                continue
        fi

        break
done

git checkout $current
