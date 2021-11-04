#!/bin/bash

# for handling library version issues, we need to keep the changes by manybug authors
cp -rf src origin

sudo apt-get update && sudo apt-get install bison -y

# reference: https://bugs.php.net/bug.php?id=55475
echo """
<?php

function __autoload(\$class) {
	echo \"Would load: \" . \$class . PHP_EOL;
}

\$var = \"test\";
var_dump(is_a(\$var, 'B'));

\$obj = new Stdclass;
var_dump(is_a(\$obj, 'C'));

?>
""" > bug.php
cd src
git checkout adabdede5e4cc039ebb7e128f3ed42fa4697c845 -f
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

	sapi/cli/php ../bug.php | grep "Would load:"
	if [[ $? == 0 ]]; then
		continue
	else
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
