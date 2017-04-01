#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# change to script dir and extend pythonpath
from sys import path as spath, argv, exit
from os import chdir, path, environ
chdir(path.dirname(__file__))
if environ['BDATBX']:
    spath.insert(0, environ['BDATBX'])
else:
    spath.insert(0, '_bdatbx_install')
if environ['BPTBX']:
    spath.insert(0, environ['BPTBX'])
else:
    spath.insert(0, '_bdatbx_install')
print('-- PYTHONPATH: {}'.format(spath))

try:
    collection_name=argv[1]
except IndexError:
    print("No collection name given.")
    exit(1)

from bdatbx import b_mongo, b_const
col = b_mongo.get_client_for_collection(collection_name, create=False)
if col is None:
    print('Collection not available.')
    exit(1)

size = b_mongo.get_collection_size(col)
modu = int(size / 100)
print('Given collection has {} elements (mod={})'.format(size, modu))

cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
i = 0
for doc in cursor:
    if ( i % modu ) == 0:
        print ('{}/{} ({}%)...'.format(i, size, (int((i/size)*100))))
        pass
    value = b_mongo.get_key_nullsafe(doc, b_const.DB_DL_RAWFILE)
    if not value:
        continue
    # --- WORK STARTS HERE
    # print (value)
    # --- WORK ENDS HERE
    i += 1
cursor.close()

def main():
    pass
