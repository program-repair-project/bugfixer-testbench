#!/bin/bash

# for handling library version issues, we need to keep the changes by manybug authors
cp -rf src origin

cd src
git checkout c5237d82bf01a762bb38f80def59b9c16cb84dc1 -f
git clean -fd
./buildconf
sed -i "s/2.4.1/2.4.1 2.4.2 2.4.3/g" configure
./configure
cp ../origin/ext/dom/* ext/dom/
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
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
make -j

sapi/cli/php ../origin/ext/pdo_sqlite/tests/bug60104.phpt
if [[ $? == 139 ]]; then
        echo "BIC found"
else
        echo "BIC not found"
fi
