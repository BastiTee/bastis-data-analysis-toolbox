#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Downloads webpages to local file from feedparse, url list or MongoDB."""

from __future__ import with_statement

from bptbx import b_iotools, b_threading, b_cmdprs
from robota import r_const, r_parse, r_mongo, r_util
from os import path
import requests
from requests import exceptions

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
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
args.i = b_cmdprs.check_opt_dir_in(
    prs, args.i, info='Input feedparse directory does not exist!')
args.l = b_cmdprs.check_opt_file_in(prs, args.l,
                                    info='Input URL list does not exist!')
col = b_cmdprs.check_mongo_collection(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------


def _worker(url, col=None, doc=None):
    file_key, dir_key = r_util.get_key_from_url(url)
    raw_fname = path.join(
        dir_key, file_key + '.' + r_const.GLOBAL_INFILE_SUFFIX)
    try:
        if b_iotools.file_exists(raw_fname):
            return
        r_mongo.set_null_safe(doc, r_const.DB_DL_DOMAIN,
                              r_parse.get_domain_from_uri(url))

        try:
            r = requests.get(url, timeout=10)
        except exceptions.TooManyRedirects as t:
            # see https://github.com/kennethreitz/requests/issues/3949
            r = requests.get(url, allow_redirects=False)
            try:
                latin1_location = r.headers['Location'].encode('latin1')
                r = requests.get(latin1_location, timeout=10)
            except KeyError:
                raise t

        statusc = r.status_code
        r_mongo.set_null_safe(doc, r_const.DB_DL_RESCODE, statusc)
        if statusc is not 200:
            return
        r_mongo.set_null_safe(doc, r_const.DB_DL_ERROR, None)

        b_iotools.mkdirs(dir_key)
        f_handle = open(raw_fname, 'w')
        f_handle.write(r.text)
        f_handle.close()

        if b_iotools.file_exists(raw_fname):
            r_mongo.set_null_safe(doc, r_const.DB_DL_RAWFILE, raw_fname)
            r_mongo.set_null_safe(doc, r_const.DB_DL_RAWFILESIZE,
                                  b_iotools.get_file_size(raw_fname))

    except Exception as e:
        r_util.log('ERROR for \'{}\': {}'.format(url, e))
        r_mongo.set_null_safe(doc, r_const.DB_DL_ERROR, str(e))
    finally:
        r_mongo.replace_doc(col, doc)
        r_util.update_progressbar()


urls = []
via_mongo = False
if args.i:
    in_files = r_util.read_valid_inputfiles(args.i)
    for in_file in in_files:
        content = ''.join(b_iotools.read_file_to_list(in_file))
        entry = r_util.json_to_object(content)
        url = entry['link']
        urls.append(url)
    r_util.log('Read {} urls from feedparse files'.format(len(urls)))
elif args.l:
    urls = b_iotools.read_file_to_list(args.l, ignore_empty_lines=True)
    r_util.log('Read {} urls from link list'.format(len(urls)))
elif args.c:
    via_mongo = True
    r_util.log('Reading from mongoDB collection \'{}\''.format(str(col)))


pool = b_threading.ThreadPool(args.t)
if not via_mongo:
    r_util.setup_progressbar(len(urls))
    for url in urls:
        pool.add_task(_worker, url)
else:
    r_util.setup_progressbar(r_mongo.get_collection_size(col))
    cursor = r_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        pool.add_task(_worker, doc[r_const.DB_SOURCE_URI], col, doc)
    cursor.close()
pool.wait_completion()
r_util.finish_progressbar()


def main():
    """Void main entry."""
    pass
