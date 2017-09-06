#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read data from MongoDB and obtain relevant keywords from text content."""

from __future__ import with_statement

import os
import nltk
from bptbx import b_iotools, b_threading, b_cmdprs
from robota import r_util, r_mongo, r_const, r_textrank

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = b_cmdprs.init('Tokenize raw text files')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
b_cmdprs.add_opt_dir_in(prs, '-n', 'Additional NLTK data directory')
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
args.n = b_cmdprs.check_opt_dir_in(prs, args.n)
b_cmdprs.check_max_threads(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------

if args.n:
    nltk.data.path.append(args.n)
    r_util.log('added nltk path {}'.format(args.n))

total_lines = []


def _worker(in_file, col=None, doc=None):
    try:
        if doc is not None:
            wc = r_mongo.get_key_nullsafe(doc, r_const.DB_TE_WC)
            if wc is None or wc < 1:
                return
        if not in_file or not b_iotools.file_exists(in_file):
            return
        text_lines = b_iotools.read_file_to_list(in_file, True)
        total_lines.append(' '.join(text_lines))

    finally:
        r_util.update_progressbar()


count = 0
pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = r_util.read_valid_inputfiles(args.i)
    count = len(in_files)
    r_util.setup_progressbar(count)
    for in_file in in_files:
        _worker(in_file)
elif col:
    query = {
        r_const.DB_LANG_AUTO: {'$eq': 'de'},
        r_const.DB_DL_DOMAIN: {'$eq': '1ppm.de'},
        r_const.DB_TE_WC: {'$gt': 50}}
    r_util.log('Query = {}'.format(query))
    count = r_mongo.count_docs(col, query)
    r_util.setup_progressbar(r_mongo.count_docs(col, query))
    cursor = r_mongo.find_docs(col, query, no_cursor_timeout=True)
    for doc in cursor:
        plain_text = r_mongo.get_key_nullsafe(doc, r_const.DB_TE_RAWFILE)
        if plain_text:
            in_file = os.path.join(args.i, plain_text)
            pool.add_task(_worker, in_file, col, doc)
    cursor.close()
pool.wait_completion()
r_util.finish_progressbar()

if count <= 0:
    r_util.log('No input data found.')
    exit(0)

intext = ' '.join(total_lines)
terms = r_textrank.score_terms_by_textrank(intext)
i = 0
for term, rank in terms:
    print('{} >> {}'.format(term, rank))
    i += 1
    if i == 25:
        break


def main():
    """Void main entry."""
    pass
