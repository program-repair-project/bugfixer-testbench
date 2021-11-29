#!/bin/bash

if [[ $1 == "gmp" ]]; then
    target_loc=""
elif [[ $1 == "libtiff" ]]; then
    if [[ $2 == "2005-12-14-6746b87-0d3d51d" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2005-12-21-3b848a7-3edb9cd" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2006-02-23-b2ce5d8-207c78a" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2006-03-03-a72cf60-0a36d7f" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2007-08-24-827b6bc-22da1d6" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2007-11-02-371336d-865f7b2" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2008-12-30-362dee5-565eaa2" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/thumbnail"
    elif [[ $2 == "2009-02-05-764dbba-2e42d63" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcrop"
    elif [[ $2 == "2009-06-30-b44af47-e0b51f3" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcp"
    elif [[ $2 == "2010-11-27-eb326f9-eec7ec0" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiff2pdf"
    elif [[ $2 == "2010-12-13-96a5fb4-bdba15c" ]]; then
      target_loc="/experiment/src/sparrow/tools/.libs/tiffcrop"
    else
      echo "Not supported"
    fi
elif [[ $1 == "php" ]]; then
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
