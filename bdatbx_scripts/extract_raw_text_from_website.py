#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Extract main textual content from HTML to text files.')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools, b_threading
from bdatbx import b_util, b_parse, b_const, b_mongo
from collections import Counter
from re import findall
import os

def worker(in_file, col=None, doc=None):
    try:
        fulltext = '\n'.join(b_iotools.read_file_to_list(in_file))
        basename = os.path.basename(in_file)
        dirn = basename[:16]
        raw_fname = os.path.join(dirn, basename)

        if not b_iotools.file_exists(raw_fname):
            b_mongo.set_null_safe(doc, b_const.DB_TE_RAWFILE, None)
            b_mongo.set_null_safe(doc, b_const.DB_TE_RAWFILESIZE, None)

            b_iotools.mkdirs(dirn)
            main_text = b_parse.extract_main_text_content(fulltext)
            if main_text:
                words = len(findall(r'[^\w]+', main_text))
                b_mongo.set_null_safe(doc, b_const.DB_TE_WC, words)

            f_handle = open(raw_fname, 'w')
            f_handle.write(main_text)
            f_handle.close()

            if b_iotools.file_exists(raw_fname):
                b_mongo.set_null_safe(
                doc, b_const.DB_TE_RAWFILE, raw_fname)
                b_mongo.set_null_safe(
                doc, b_const.DB_TE_RAWFILESIZE, b_iotools.get_file_size(raw_fname))
    finally:
        b_mongo.replace_doc(col, doc)
        b_util.update_progressbar()

pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = b_util.read_valid_inputfiles(args.i)
    b_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        pool.add_task(worker, in_file)
else:
    b_util.setup_progressbar(b_mongo.get_collection_size(col))
    cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        html_file = b_mongo.get_key_nullsafe(doc, b_const.DB_DL_RAWFILE)
        if html_file:
            in_file = os.path.join(args.i, html_file)
            pool.add_task(worker, in_file, col, doc)
    cursor.close()

pool.wait_completion()
b_util.finish_progressbar()

def main():
    pass
