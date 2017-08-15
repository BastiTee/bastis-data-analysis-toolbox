#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Go through each document of a MongoDB collection and manipulate doc."""

from sys import argv
try:
    collection_name = argv[1]
except IndexError:
    print("No collection name given.")
    exit(1)

from robota import r_mongo, r_const
col = r_mongo.get_client_for_collection(collection_name, create=False)
if col is None:
    print('Collection not available.')
    exit(1)

size = r_mongo.get_collection_size(col)
modu = int(size / 100)
print('Given collection has {} elements (mod={})'.format(size, modu))

cursor = r_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
i = 0
for doc in cursor:
    if (i % modu) == 0:
        print('{}/{} ({}%)...'.format(i, size, (int((i / size) * 100))))
    i += 1
    value = r_mongo.get_key_nullsafe(doc, r_const.DB_DL_RAWFILE)
    if not value:
        continue

    # --- WORK STARTS HERE

    # ...

    # --- WORK ENDS HERE

cursor.close()


def main():
    """Void main entry."""
    pass
