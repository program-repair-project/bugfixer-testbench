#!/bin/bash

# for handling library version issues, we need to keep the changes by manybug authors
cp -rf src origin

cd src
git checkout cc1c7af0375db5b7ad2c7752569b925cc3372377 -f
cp ../origin/ext/dom/* ext/dom/
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
cp ../origin/Zend/zend_modules.h Zend/zend_modules.h
cp ../origin/main/php.h main/php.h
make -j

sapi/cli/php ext/standard/tests/general_functions/get_magic_quotes_gpc.phpt | grep "Deprecated: Function get_magic_quotes_gpc() is deprecated"
if [[ $? == 0 ]]; then
        echo "BIC found"
else
        echo "BIC not found"
fi
