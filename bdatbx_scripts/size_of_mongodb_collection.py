#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
try:
    collection_name=sys.argv[1]
except IndexError:
    sys.exit(1)

# change to script dir and extend pythonpath
from sys import path as spath
from os import chdir, path
chdir(path.dirname(__file__))
spath.insert(0, '_bdatbx_install')
spath.insert(0, '_bptbx_install')

from bdatbx import b_mongo
col = b_mongo.get_client_for_collection(collection_name, create=False)
if col is None:
    print('0')
size = b_mongo.get_collection_size(col)
print(size)

def main():
    pass
