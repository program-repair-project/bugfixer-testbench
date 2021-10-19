#!/bin/bash

sudo apt-get install -y texinfo

cd /experiment/src
hg update -C -r 14162
