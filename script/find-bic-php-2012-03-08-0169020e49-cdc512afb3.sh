#!/bin/bash

# for handling library version issues, we need to keep the changes by manybugs authors
cp -rf src origin

sudo apt-get update && sudo apt-get install bison -y

cd src
current=cdc512afb39f7da84a798f7702b1cc4de3524463
git checkout $current -f
./buildconf >/dev/null 2>&1
sed -i "s/2.4.1 2.4.2/2.4.1 2.4.2 2.4.3/g" configure
./configure >/dev/null 2>&1

while true; do
    current=$(git log -n1 --pretty=format:"%H")
    parent=$(git log -n1 --pretty=format:"%P")
    echo $parent
    git checkout $parent -f
    cp ../origin/ext/dom/* ext/dom/
    cp ../origin/ext/simplexml/* ext/simplexml/
    cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
    sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
    sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
    sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
    make clean && make -j >/dev/null 2>&1

    cp -r ../origin/ext/phar/tests/* ext/phar/

    sapi/cli/php run-tests.php -p sapi/cli/php ext/phar/tests/017.phpt | grep "FAIL Phar:"
    if [[ $? == 0 ]]; then
        echo $current "is not BIC"
        continue
    fi

    sapi/cli/php run-tests.php -p sapi/cli/php ext/phar/tests/027.phpt | grep "FAIL Phar:"
    if [[ $? == 0 ]]; then
        echo $current "is not BIC"
        continue
    fi

    sapi/cli/php run-tests.php -p sapi/cli/php ext/phar/tests/opendir.phpt | grep "FAIL Phar:"
    if [[ $? == 0 ]]; then
        echo $current "is not BIC"
        continue
    fi

    sapi/cli/php run-tests.php -p sapi/cli/php ext/phar/tests/tar/tar_nostub.phpt | grep "FAIL Phar:"
    if [[ $? == 0 ]]; then
        echo $current "is not BIC"
        continue
    fi

    echo $current "is BIC"
    break
done
git checkout $current -f
cp ../origin/ext/dom/* ext/dom/
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
make clean && make -j
