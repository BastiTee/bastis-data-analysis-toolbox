#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement

# export PYTHONPATH=${PYTHONPATH}:. && bdatbx_scripts/get-keywords.py -i ../bonnerblogs-analysis/_bonndigital_2016-11-06.full-plain-text/ -o _keywords/ -c bonndigital_2016-11-06.full -n nltk-data/
# {"__lang_auto": {"$eq": "de"}, "__src_tags": {"$eq": ["Bonn"]}, "__te_tokencount": {"$gt": 500}}

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs, b_util
b_util.notify_start(__file__)
prs = b_cmdprs.init('Tokenize raw text files')
b_cmdprs.add_dir_in(prs)
# b_cmdprs.add_dir_out(prs)
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

import os
import nltk
from bptbx import b_iotools, b_threading
from bdatbx import b_lists, b_util, b_mongo, b_const
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
if args.n:
    nltk.data.path.append(args.n)
    b_util.log('added nltk path {}'.format(args.n))

total_lines = []

def worker(in_file, col=None, doc=None):
    try:
        # when using mongo, check if word count is relevant
        if doc is not None:
            wc = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_WC)
            if wc is None or wc < 1:
                return
        # check if input file is present
        if not in_file or not b_iotools.file_exists(in_file):
            return
        # generate output paths
        # basename = os.path.basename(in_file)
        # dirn = basename[:16]
        # raw_fname = os.path.join(dirn, basename)
        # if b_iotools.file_exists(raw_fname):
        #     return
        # b_iotools.mkdirs(dirn)
        text_lines = b_iotools.read_file_to_list(in_file, True)
        total_lines.append(' '.join(text_lines))

    finally:
        # b_mongo.replace_doc(col, doc)
        b_util.update_progressbar()

count = 0
pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = b_util.read_valid_inputfiles(args.i)
    count = len(in_files)
    b_util.setup_progressbar(count)
    for in_file in in_files:
        worker(in_file)
elif col:
    query = {
        b_const.DB_LANG_AUTO: {"$eq": "de"},
        b_const.DB_DL_DOMAIN: {"$eq": "1ppm.de"},
        b_const.DB_TE_WC: {"$gt": 50}}
    b_util.log('Query = {}'.format(query))
    count = b_mongo.count_docs(col, query)
    b_util.setup_progressbar(b_mongo.count_docs(col, query))
    cursor = b_mongo.find_docs(col, query, no_cursor_timeout=True)
    for doc in cursor:
        plain_text = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_RAWFILE)
        if plain_text:
            in_file = os.path.join(args.i, plain_text)
            pool.add_task(worker, in_file, col, doc)
    cursor.close()
pool.wait_completion()
b_util.finish_progressbar()

if count <= 0:
    b_util.log('No input data found.')
    exit(0)

intext = ' '.join(total_lines)
from bdatbx import b_textrank
terms = b_textrank.score_terms_by_textrank(intext)
i = 0
for term, rank in terms:
    print('{} >> {}'.format(term, rank))
    i += 1
    if i == 25:
        break


def main():
    pass
