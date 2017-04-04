#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Go through each document of a MongoDB collection and manipulate doc.

python3 -m bdatbx_scripts.extract_pubdate_from_html.py
bonndigital_2016-11-06.sanity

python3 -m bdatbx.b_date_extractor "<url>"
"""

from sys import argv
from bdatbx import b_mongo, b_const, b_date_extractor
from bptbx import b_iotools

try:
    collection_name = argv[1]
except IndexError:
    print("No collection name given.")
    exit(1)

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
    if (i % modu) == 0:
        # print('{}/{} ({}%)...'.format(i, size, (int((i / size) * 100))))
        pass
    i += 1

    raw_html = b_mongo.get_key_nullsafe(doc, b_const.DB_DL_RAWFILE)
    url = b_mongo.get_key_nullsafe(doc, b_const.DB_SOURCE_URI)

    if not raw_html or not url:
        continue

    raw_file = ('/data/github/bonnerblogs-analysis/' +
                '_bonndigital_2016-11-06.sanity-raw-html/' + raw_html)
    raw_html = '\n'.join(b_iotools.read_file_to_list(raw_file))

    date, hint = b_date_extractor.extract_article_pubdate(url, raw_html)
    if not hint:
        hint = '??'
    if not date:
        date = '??'
    print('{} | {} | {}'.format(hint.ljust(8), str(date).ljust(25), url[:80]))

cursor.close()


def main():
    """Void main entry."""
    pass
