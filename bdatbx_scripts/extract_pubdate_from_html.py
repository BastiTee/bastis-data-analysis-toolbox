#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracts the raw main text content from an HTML page."""

from __future__ import with_statement
from bptbx import b_iotools, b_threading
from bdatbx import b_const, b_mongo, b_cmdprs, b_util, b_date_extractor
import os

# ------------------------------------------------------------ CMD-LINE-PARSING
b_util.notify_start(__file__)
prs = b_cmdprs.init('Extract main textual content from HTML to text files.')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_bool(prs, '-f', 'Only print out URLs with no date extracted.')
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_max_threads(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------


def _worker(in_file, col=None, doc=None):
    try:
        raw_html = '\n'.join(b_iotools.read_file_to_list(in_file))
        url = b_mongo.get_key_nullsafe(doc, b_const.DB_SOURCE_URI)
        if not url:
            url = ''
            print(url)
        date, hint = b_date_extractor.extract_article_pubdate(url, raw_html)

        if args.f and not hint:
            print(url)
        elif not args.f:
            print('{} | {} | {}'.format(
                str(hint).ljust(8), str(date).ljust(25), url[:80]))
    finally:
        pass
        # b_mongo.replace_doc(col, doc)
        # b_util.update_progressbar()


pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = b_util.read_valid_inputfiles(args.i)
    # b_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        pool.add_task(_worker, in_file)
else:
    b_util.setup_progressbar(b_mongo.get_collection_size(col))
    cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        html_file = b_mongo.get_key_nullsafe(doc, b_const.DB_DL_RAWFILE)
        if html_file:
            in_file = os.path.join(args.i, html_file)
            pool.add_task(_worker, in_file, col, doc)
    cursor.close()

pool.wait_completion()
# b_util.finish_progressbar()


def main():
    """Void main entry."""
    pass
