#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Returns the size of the given MongoDB collection or 0 if not present."""

from sys import argv
from robota import r_mongo

try:
    collection_name = argv[1]
except IndexError:
    print("No collection name given.")
    exit(1)

col = r_mongo.get_client_for_collection(collection_name, create=False)
if col is None:
    print('0')
    exit(1)
size = r_mongo.get_collection_size(col)
print(size)


def main():
    """Void main entry."""
    pass
