#!/bin/bash

# for handling library version issues, we need to keep the changes by manybug authors
cp -rf src origin

sudo apt-get update && sudo apt-get install bison -y

# reference: https://bugs.php.net/bug.php?id=55475
echo """
<?php
 echo html_entity_decode('&OElig;', 0, 'ISO-8859-1');
?>
""" > bug.php
cd src
git checkout 4a946a91e5d0e431126e38bf53efce75d7b66324 -f
./buildconf
sed -i "s/2.4.1 2.4.2/2.4.1 2.4.2 2.4.3/g" configure
./configure

while true; do
	current=`git log -n1 --pretty=format:"%H"`
        parent=`git log -n1 --pretty=format:"%P"`
        echo $parent
        git checkout $parent -f
	cp ../origin/ext/dom/* ext/dom/
	cp ../origin/ext/simplexml/* ext/simplexml/
	cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
	sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
	sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
	sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
	make clean && make -j

	sapi/cli/php ../bug.php | grep "&OElig"
	if [[ $? == 0 ]]; then
		break
	fi
done
git checkout $current -f
cp ../origin/ext/dom/* ext/dom/
cp ../origin/ext/simplexml/* ext/simplexml/
cp ../origin/ext/xmlreader/php_xmlreader.c ext/xmlreader/php_xmlreader.c
sed -i "s/#define PHP_ME_MAPPING  ZEND_ME_MAPPING/#define PHP_ME_MAPPING  ZEND_ME_MAPPING\n#define PHP_FE_END      ZEND_FE_END/g" main/php.h
sed -i "s/#define ZEND_ARG_INFO(pass_by_ref, name)/#define ZEND_FE_END            { NULL, NULL, NULL, 0, 0 }\n#define ZEND_ARG_INFO(pass_by_ref, name)/g" Zend/zend_API.h
sed -i "s/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)/ZEND_MOD_OPTIONAL_EX(name, NULL, NULL)\n#define ZEND_MOD_END { NULL, NULL, NULL, 0 }/g" Zend/zend_modules.h
make clean && make -j
