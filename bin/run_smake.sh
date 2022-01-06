#!/bin/bash

function checkout_php_parent_a() {
  git checkout HEAD~1 -f
  git clean -fd
  ./buildconf
  sed -i "s/2.4.1/2.4.1 2.4.2 2.4.3/g" configure
  ./configure
  cp $OUTDIR/bic/src/ext/dom/node.c ext/dom/node.c
  cp $OUTDIR/bic/src/ext/dom/documenttype.c ext/dom/documenttype.c
  cp $OUTDIR/bic/src/ext/simplexml/* ext/simplexml/
  cp $OUTDIR/bic/src/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
  sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
  sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
  sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
  git checkout -- ext/xmlreader/php_xmlreader.c ext/dom/php_dom.c ext/dom/php_dom.h
  sed -i "s/, zval \*return_value/, zval \*in, zval \*return_value/g" ext/dom/php_dom.c
  sed -i "s/wrapper_in, zval \*//g" ext/dom/php_dom.c
  sed -i "s/wrapper_in, zval \*//g" ext/dom/php_dom.h
  git checkout -- ext/simplexml/simplexml.c
  sed -i "s/outbuf->buffer->content/xmlOutputBufferGetContent(outbuf)/g" ext/simplexml/simplexml.c
  sed -i "s/outbuf->buffer->use/xmlOutputBufferGetSize(outbuf)/g" ext/simplexml/simplexml.c
  git checkout -- ext/simplexml/sxe.c
}

function checkout_php_parent_b() { 
  git checkout HEAD~1 -f
  git clean -fd
  ./buildconf
  sed -i "s/2.4.1/2.4.1 2.4.2 2.4.3/g" configure
  ./configure

  cp $OUTDIR/bic/src/ext/dom/* ext/dom/
  cp $OUTDIR/bic/src/ext/simplexml/* ext/simplexml/
  cp $OUTDIR/bic/src/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
  sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
  sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
  sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
  git checkout -- ext/xmlreader/php_xmlreader.c
  sed -i "s/DOM_RET_OBJ(rv, nodec,/DOM_RET_OBJ(nodec,/g" ext/xmlreader/php_xmlreader.c
  git checkout -- ext/dom/php_dom.c
  sed -i "s/DOM_RET_OBJ(rv,/DOM_RET_OBJ(/g" ext/dom/php_dom.c
  sed -i "s/wrapper_in, zval \*//g" ext/dom/php_dom.c
  git checkout -- ext/simplexml/simplexml.c
  sed -i "s/outbuf->buffer->content/xmlOutputBufferGetContent(outbuf)/g" ext/simplexml/simplexml.c
  sed -i "s/outbuf->buffer->use/xmlOutputBufferGetSize(outbuf)/g" ext/simplexml/simplexml.c
  git checkout -- ext/simplexml/sxe.c
}

function checkout_php_parent_c(){
  git checkout HEAD~1 -f
  git clean -fd
  ./buildconf
  sed -i "s/2.4.1 2.4.2/2.4.1 2.4.2 2.4.3/g" configure
  ./configure

  cp $OUTDIR/bic/src/ext/dom/node.c ext/dom/node.c
  cp $OUTDIR/bic/src/ext/dom/documenttype.c ext/dom/documenttype.c
	cp $OUTDIR/bic/src/ext/simplexml/* ext/simplexml/
	cp $OUTDIR/bic/src/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
	sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
	sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
	sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
	
}

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
      exit
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


    if   [[ $2 == "2011-01-18-95388b7cda-b9b1fb1827" ]] ||
         [[ $2 == "2011-02-21-2a6968e43a-ecb9d8019c" ]] ||
         [[ $2 == "2011-03-11-d890ece3fc-6e74d95f34" ]] ||
         [[ $2 == "2011-03-27-11efb7295e-f7b7b6aa9e" ]] ||
         [[ $2 == "2011-04-07-d3274b7f20-77ed819430" ]] ; then
      checkout_php_parent_a
    elif [[ $2 == "2011-10-31-c4eb5f2387-2e5d5e5ac6" ]] ||
         [[ $2 == "2011-11-08-0ac9b9b0ae-cacf363957" ]] ||
         [[ $2 == "2011-12-04-1e6a82a1cf-dfa08dc325" ]] ; then
      checkout_php_parent_b
    elif [[ $2 == "2011-11-19-eeba0b5681-f330c8ab4e" ]] ||
         [[ $2 == "2012-03-08-0169020e49-cdc512afb3" ]] ; then
      checkout_php_parent_c
    elif [[ $2 == "2012-03-12-7aefbf70a8-efc94f3115" ]] || 
         [[ $2 == "2011-11-11-fcbfbea8d2-c1e510aea8" ]] ||
         [[ $2 == "2011-11-08-c3e56a152c-3598185a74" ]] ; then
      echo "Not supported"
      exit
    fi

    rm -rf sparrow
    make clean
    cp -rf /experiment/src $OUTDIR/parent/src
    yes | /bugfixer/smake/smake --init
    /bugfixer/smake/smake -j
    cp -r $target_loc $OUTDIR/parent/smake-out
    
else
  echo "Not supported"
fi