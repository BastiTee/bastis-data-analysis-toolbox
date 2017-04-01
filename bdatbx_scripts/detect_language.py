#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import langdetect
from bptbx.b_iotools import read_file_to_list
from bptbx import b_threading
from bdatbx import b_util
from os import path
from re import findall
from bdatbx.b_const import GLOBAL_INFILE_SUFFIX

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs, b_const
prs = b_cmdprs.init(
    'Detect (or best-guess) the language of the given file\'s content')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_file_out(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_file_out(prs, args)
if args.c:
    from bdatbx import b_mongo
    col = b_mongo.get_client_for_collection(args.c, create=False)
    if not col:
        b_cmdprs.show_help(
            prs, 'You provided a mongo collection that doesn\'t exist.')

# -----------------------------------------------------------------------------

f_handle = open(args.o, 'w')

def worker(filepath, col=None, doc=None):
    try:
        b_mongo.set_null_safe(doc, b_const.DB_LANG_AUTO, None)
        file_key, dir_key = b_util.get_key_from_url(filepath)
        raw_fname = path.join(dir_key, file_key + '.' + GLOBAL_INFILE_SUFFIX)
        in_text = ' '.join(read_file_to_list(filepath))
        words = len(findall(r'[^\w]+', in_text))
        if words < 10:
            return
        lang = langdetect.detect(in_text)
        if lang:
            b_mongo.set_null_safe(doc, b_const.DB_LANG_AUTO, lang)
        f_handle.write('{} {}\n'.format(lang, raw_fname))
    finally:
        b_mongo.replace_doc(col, doc)
        b_util.update_progressbar()

pool = b_threading.ThreadPool(1)
if args.i and not args.c:
    in_files = b_util.read_valid_inputfiles(args.i)
    b_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        pool.add_task(worker, in_file)
elif args.c:
    b_util.setup_progressbar(b_mongo.get_collection_size(col))
    cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    i = 0
    for doc in cursor:
        html_file = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_RAWFILE)
        if html_file:
            in_file = path.join(args.i, html_file)
            pool.add_task(worker, in_file, col, doc)
        i += 1
    cursor.close()
    b_util.log('Cursor closed. Added {} jobs to job queue.'.format(i))

pool.wait_completion()
b_util.finish_progressbar()
f_handle.close()

def main():
    pass
