#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatically detect the language of the provided text samples."""

import langdetect
from bptbx import b_threading, b_iotools
from os import path
from re import findall
from robota import r_cmdprs, r_const, r_util, r_mongo

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = r_cmdprs.init(
    'Detect (or best-guess) the language of the given file\'s content')
r_cmdprs.add_dir_in(prs)
r_cmdprs.add_mongo_collection(prs)
r_cmdprs.add_file_out(prs)
args = prs.parse_args()
r_cmdprs.check_dir_in(prs, args)
r_cmdprs.check_file_out(prs, args)
col = r_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------


def _worker(filepath, col=None, doc=None):
    try:
        r_mongo.set_null_safe(doc, r_const.DB_LANG_AUTO, None)
        file_key, dir_key = r_util.get_key_from_url(filepath)
        raw_fname = path.join(dir_key, file_key + '.' +
                              r_const.GLOBAL_INFILE_SUFFIX)
        in_text = ' '.join(b_iotools.read_file_to_list(filepath))
        words = len(findall(r'[^\w]+', in_text))
        if words < 10:
            return
        lang = langdetect.detect(in_text)
        if lang:
            r_mongo.set_null_safe(doc, r_const.DB_LANG_AUTO, lang)
        f_handle.write('{} {}\n'.format(lang, raw_fname))
    finally:
        r_mongo.replace_doc(col, doc)
        r_util.update_progressbar()


f_handle = open(args.o, 'w')
pool = b_threading.ThreadPool(1)
if args.i and not col:
    in_files = r_util.read_valid_inputfiles(args.i)
    r_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        pool.add_task(_worker, in_file)
else:
    r_util.setup_progressbar(r_mongo.get_collection_size(col))
    cursor = r_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        html_file = r_mongo.get_key_nullsafe(doc, r_const.DB_TE_RAWFILE)
        if html_file:
            in_file = path.join(args.i, html_file)
            pool.add_task(_worker, in_file, col, doc)
    cursor.close()

pool.wait_completion()
r_util.finish_progressbar()
f_handle.close()


def main():
    """Void main entry."""
    pass
