#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Tokenize raw text files')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
b_cmdprs.add_opt_dir_in(prs, '-n', 'Additional NLTK data directory')
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
args.n = b_cmdprs.check_opt_dir_in(prs, args.n)
b_cmdprs.check_dir_out_and_chdir(prs, args)
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
from rake_nltk import Rake
r = Rake()

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
        basename = os.path.basename(in_file)
        dirn = basename[:16]
        raw_fname = os.path.join(dirn, basename)
        if b_iotools.file_exists(raw_fname):
            return
        b_iotools.mkdirs(dirn)
        # ------------------------------------------------

        text_lines = b_iotools.read_file_to_list(in_file, True)
        total_lines.append(' '.join(text_lines))
        # r.extract_keywords_from_text(text_lines)
        # print(r.get_ranked_phrases())

        # ------------------------------------------------
        # b_iotools.write_list_to_file(tokens, raw_fname)
        # if b_iotools.file_exists(raw_fname):
        #     b_mongo.set_null_safe(doc, b_const.DB_TOK_RAWFILE, raw_fname)
        #     b_mongo.set_null_safe(doc, b_const.DB_TOK_RAWFILESIZE,
        #     b_iotools.get_file_size(raw_fname))
        # ------------------------------------------------
    finally:
        # b_mongo.replace_doc(col, doc)
        b_util.update_progressbar()

pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = b_util.read_valid_inputfiles(args.i)
    b_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        worker(in_file)
elif col:
    # query = { "__lang_auto": { "$eq": "de" } }
    query = { "__lang_auto": { "$eq": "de" },"__src_tags": { "$eq": ["Persönlich"] } }
    b_util.setup_progressbar(b_mongo.count_docs(col, query))
    # cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    cursor = b_mongo.find_docs(col, query, no_cursor_timeout=True)
    for doc in cursor:
        plain_text = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_RAWFILE)
        if plain_text:
            in_file = os.path.join(args.i, plain_text)
            pool.add_task(worker, in_file, col, doc)
    cursor.close()
pool.wait_completion()
b_util.finish_progressbar()

intext = ' '.join(total_lines)
from bdatbx import b_textrank
terms = b_textrank.score_terms_by_textrank(intext)
i = 0
for term, rank in terms:
    print('{} >> {}'.format(term, rank))
    i += 1
    if i == 15:
        break

def main():
    pass
