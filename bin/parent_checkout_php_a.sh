#!/bin/bash

cd /experiment
cp -rf src origin
cd /experiment/src
git checkout HEAD~1 -f
git clean -fd
./buildconf
sed -i "s/2.4.1/2.4.1 2.4.2 2.4.3/g" configure
./configure
cp ../origin/ext/dom/node.c ext/dom/node.c
cp ../origin/ext/dom/documenttype.c ext/dom/documenttype.c
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
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
sed -i "s/ \$pharcmd"/"/g" /experiment/src/configure
sed -i "s/alias(\"zend_error\"),//g" /experiment/src/Zend/zend.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/Zend/*.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/Zend/*.h
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/ext/standard/*.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/ext/standard/*.h
cd /experiment/bic
make clean && ./configure
cd /experiment/src
make clean && ./configure
cd /experiment
./line_matching.py "./src/" "./bic/"
cd /experiment
