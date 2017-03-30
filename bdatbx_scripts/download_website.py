#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init(
    'Dump website content of given feedparse run / linklist to text files. ' +
    'WARN: Options -i, -l, -c are mutual exclusive with ' +
    'Priority: Directory -> URL File -> MongoDB')
b_cmdprs.add_dir_in(prs, label='Input directory (feedparse files)')
b_cmdprs.add_opt_file_in(prs, '-l', 'Flat input URL list')
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
args.i = b_cmdprs.check_opt_dir_in(prs, args.i,
                                   info='Input feedparse directory does not exist!')
args.l = b_cmdprs.check_opt_file_in(prs, args.l,
                                    info='Input URL list does not exist!')
if args.c:
    from bdatbx import b_mongo
    col = b_mongo.get_client_for_collection(args.c, create=False)
    if not col:
        b_cmdprs.show_help(
            prs, 'You provided a mongo collection that doesn\'t exist.')
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools, b_threading
from bdatbx import b_util, b_const, b_parse, b_mongo
from os import path
from re import search
import time
import requests
import feedparser


def worker(url, col=None, doc=None):
    file_key, dir_key = b_util.get_key_from_url(url)
    raw_fname = path.join(
        dir_key, file_key + '.' + b_const.GLOBAL_INFILE_SUFFIX)

    if b_iotools.file_exists(raw_fname):
        b_util.update_progressbar()
        return

    b_mongo.update_value_nullsafe(col, doc, b_const.DB_DL_DOMAIN,
                                  b_parse.get_domain_from_uri(url))
    try:
        b_mongo.update_value_nullsafe(
            col, doc, b_const.DB_DL_RESCODE)
        r = requests.get(url, timeout=10)
        res_code = r.status_code
        b_mongo.update_value_nullsafe(
            col, doc, b_const.DB_DL_RESCODE, res_code)
    except Exception as e:
        b_util.log('ERROR for \'{}\': {}'.format(url, e))
        b_util.update_progressbar()
        return
    if res_code is not 200:
        b_util.update_progressbar()
        return

    # filter out spiegel plus content for now
    # (deobfuscation will be applied soon)
    if (
        search('www\.spiegel\.de', r.text) and
        search('<p[ ]+class=\"obfuscated\"[ ]*>', r.text)
    ):
        b_util.log(
            'WARN: \'{}\' skipped because of missing deobfuscation of spiegel-plus content'.format(url))
        b_util.update_progressbar()
        return

    b_iotools.mkdirs(dir_key)

    f_handle = open(raw_fname, 'w')
    f_handle.write(r.text)
    f_handle.close()

    if b_iotools.file_exists(raw_fname):
        b_mongo.update_value_nullsafe(
            col, doc, b_const.DB_DL_RAWFILE, raw_fname)
        b_mongo.update_value_nullsafe(
            col, doc, b_const.DB_DL_RAWFILESIZE,                                      b_iotools.get_file_size(raw_fname))
    b_util.update_progressbar()

urls = []
via_mongo = False
if args.i:
    in_files = b_util.read_valid_inputfiles(args.i)
    for in_file in in_files:
        content = ''.join(b_iotools.read_file_to_list(in_file))
        entry = b_util.json_to_object(content)
        url = entry['link']
        urls.append(url)
    b_util.log('Read {} urls from feedparse files'.format(len(urls)))
elif args.l:
    urls = b_iotools.read_file_to_list(args.l)
    b_util.log('Read {} urls from link list'.format(len(urls)))
elif args.c:
    via_mongo = True
    b_util.log('Reading from mongoDB collection \'{}\''.format(str(col)))


pool = b_threading.ThreadPool(args.t)
if not via_mongo:
    b_util.setup_progressbar(len(urls))
    for url in urls:
        pool.add_task(worker, url)
else:
    b_util.setup_progressbar(b_mongo.get_collection_size(col))
    for doc in b_mongo.get_snapshot_cursor(col):
        pool.add_task(worker, doc[b_const.DB_SOURCE_URI], col, doc)
pool.wait_completion()
b_util.finish_progressbar()


def main():
    pass
