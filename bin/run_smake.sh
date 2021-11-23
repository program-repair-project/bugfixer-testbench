#!/bin/bash

if [[ $1 == "libtiff" ]]; then
    target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
elif [[ $1 == "gmp" ]]; then
    target_loc=""
else
  echo "Not supported"
fi


mkdir /experiment/smake-out
cd /experiment/src
make clean
/bugfixer/smake/smake --init
/bugfixer/smake/smake -j
cp -r $target_loc ../smake-out/bic

git reset --hard HEAD~1
rm -r sparrow
make clean
/bugfixer/smake/smake --init
/bugfixer/smake/smake -j
cp -r $target_loc ../smake-out/parent