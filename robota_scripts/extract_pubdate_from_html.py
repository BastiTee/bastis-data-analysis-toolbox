#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracts the raw main text content from an HTML page."""

from __future__ import with_statement
from bptbx import b_iotools, b_threading
from robota import r_const, r_mongo, r_cmdprs, r_util, r_date_extractor
import os

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = r_cmdprs.init('Extract main textual content from HTML to text files.')
r_cmdprs.add_dir_in(prs)
r_cmdprs.add_mongo_collection(prs)
r_cmdprs.add_max_threads(prs)
r_cmdprs.add_bool(prs, '-f', 'Only print out URLs with no date extracted.')
args = prs.parse_args()
r_cmdprs.check_dir_in(prs, args)
r_cmdprs.check_max_threads(prs, args)
col = r_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------


def _worker(in_file, col=None, doc=None):
    try:
        raw_html = '\n'.join(b_iotools.read_file_to_list(in_file))
        url = r_mongo.get_key_nullsafe(doc, r_const.DB_SOURCE_URI)
        if not url:
            url = ''
            print(url)
        date, hint = r_date_extractor.extract_article_pubdate(url, raw_html)

        if args.f and not hint:
            print(url)
        elif not args.f:
            print('{} | {} | {}'.format(
                str(hint).ljust(8), str(date).ljust(25), url[:80]))
    finally:
        pass
        # r_mongo.replace_doc(col, doc)
        # r_util.update_progressbar()


pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = r_util.read_valid_inputfiles(args.i)
    # r_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        pool.add_task(_worker, in_file)
else:
    r_util.setup_progressbar(r_mongo.get_collection_size(col))
    cursor = r_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        html_file = r_mongo.get_key_nullsafe(doc, r_const.DB_DL_RAWFILE)
        if html_file:
            in_file = os.path.join(args.i, html_file)
            pool.add_task(_worker, in_file, col, doc)
    cursor.close()

pool.wait_completion()
# r_util.finish_progressbar()


def main():
    """Void main entry."""
    pass
