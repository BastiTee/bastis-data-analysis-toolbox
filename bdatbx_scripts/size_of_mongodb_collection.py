#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sys import argv
try:
    collection_name=argv[1]
except IndexError:
    print("No collection name given.")
    exit(1)

from bdatbx import b_mongo
col = b_mongo.get_client_for_collection(collection_name, create=False)
if col is None:
    print('0')
    exit(1)
size = b_mongo.get_collection_size(col)
print(size)

def main():
    pass
