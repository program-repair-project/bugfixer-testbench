#!/bin/bash

# for handling library version issues, we need to keep the changes by manybug authors
cp -rf src origin

sudo apt-get update && sudo apt-get install bison -y
cd src
git checkout b4368a76cd1090184732602a8ecaadf8f824c9dc -f
./buildconf
sed -i "s/2.4.1 2.4.2/2.4.1 2.4.2 2.4.3/g" configure
cp ../origin/ext/dom/* ext/dom/
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
./configure && make clean && make -j

sapi/cli/php ../origin/ext/phar/tests/bug60261.phpt
if [[ $? == 139 ]]; then
        echo "BIC found"
else
        echo "BIC not found"
fi
