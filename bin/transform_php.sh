#!/bin/bash

sed -i "s/ \$pharcmd"/"/g" /experiment/src/configure
sed -i "s/alias(\"zend_error\"),//g" /experiment/src/Zend/zend.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/Zend/*.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/Zend/*.h
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/ext/standard/*.c
sed -i "s/zend_error_noreturn/zend_error/g" /experiment/src/ext/standard/*.h
sed -i 's/"sapi\/cli\/php", "run-tests.php", "-p", //g' /experiment/tester.py 
sed -i 's/60/5/g' /experiment/tester.py 
sed -i 's/\/experiment/timeout 5 \/experiment/g' /experiment/test.sh
