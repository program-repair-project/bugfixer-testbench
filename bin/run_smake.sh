#!/bin/bash

OUTDIR=/experiment/$1-$2
mkdir $OUTDIR
mkdir $OUTDIR/bic
mkdir $OUTDIR/parent

if [[ $1 == "gmp" ]]; then
    target_loc="/experiment/src/sparrow/.libs/libgmp.so.10.0.1"
    cd /experiment/src
    make clean
    cp -rf /experiment/src $OUTDIR/bic/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/bic/smake-out
    rm -r /experiment/src/sparrow

    cd /experiment/src/tests/mpz
    yes | /bugfixer/smake/smake --init
    if [[ $2 == "13420-13421" ]]; then
      /bugfixer/smake/smake t-powm
      cp /experiment/src/tests/mpz/sparrow/t-powm.o.i $OUTDIR/bic/smake-out
      rm -r /experiment/src/tests/mpz/sparrow

      cd /experiment/src
      hg update -C -r 13418
    elif [[ $2 == "14166-14167" ]]; then
      /bugfixer/smake/smake t-gcd
      cp /experiment/src/tests/mpz/sparrow/t-gcd.o.i $OUTDIR/bic/smake-out
      rm -r /experiment/src/tests/mpz/sparrow

      cd /experiment/src
      hg update -C -r 14161
    fi

    make clean
    cp -rf /experiment/src $OUTDIR/parent/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/parent/smake-out

    cd /experiment/src/tests/mpz
    yes | /bugfixer/smake/smake --init
    if [[ $2 == "13420-13421" ]]; then
      /bugfixer/smake/smake t-powm
      cp /experiment/src/tests/mpz/sparrow/t-powm.o.i $OUTDIR/parent/smake-out
    elif [[ $2 == "14166-14167" ]]; then
      /bugfixer/smake/smake t-gcd
      cp /experiment/src/tests/mpz/sparrow/t-gcd.o.i $OUTDIR/parent/smake-out
    fi

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

    cd /experiment/src
    make clean
    cp -rf /experiment/src $OUTDIR/bic/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/bic/smake-out

    ## Todo: checking out to parent differs by projects. Generalize this process.
    git reset --hard HEAD~1
    rm -rf sparrow
    make clean
    cp -rf /experiment/src $OUTDIR/parent/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/parent/smake-out

elif [[ $1 == "php" ]]; then
    target_loc="/experiment/src/sparrow/sapi/cli/php"
    cd /experiment/src
    make clean
    cp -rf /experiment/src $OUTDIR/bic/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/bic/smake-out

    ## Todo: checking out to parent differs by projects. Generalize this process.
    git reset --hard HEAD~1
    rm -rf sparrow
    make clean
    cp -rf /experiment/src $OUTDIR/parent/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/parent/smake-out
else
  echo "Not supported"
fi
