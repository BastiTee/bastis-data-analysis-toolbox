#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init(
    'Dump website content of given feedparse run / linklist to text files')
b_cmdprs.add_dir_in(prs, label='Input directory (feedparse files)')
b_cmdprs.add_opt_file_in(prs, '-l', 'Flat input URL list (replaces -i option)')
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
args.i = b_cmdprs.check_opt_dir_in(prs, args.i,
                                   info='Input feedparse directory does not exist!')
args.l = b_cmdprs.check_opt_file_in(prs, args.l,
                                    info='Input URL list does not exist!')
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools, b_threading
from os import path
from re import search
import time
import requests
from bdatbx import b_util
from bdatbx.b_util import GLOBAL_INFILE_SUFFIX
import feedparser


def worker(url):
    file_key, dir_key = b_util.get_key_from_url(url)
    raw_fname = path.join(dir_key, file_key + '.' + GLOBAL_INFILE_SUFFIX)

    if not b_iotools.file_exists(raw_fname):
        try:
            r = requests.get(url, timeout=10)
            res_code = r.status_code
        except Exception as e:
            b_util.log('ERROR for \'{}\': {}'.format(url, e))
            b_util.update_progressbar()
            return
        if res_code is not 200:
            b_util.update_progressbar()
            return

        # filter out spiegel plus content for now
        # (deobfuscation will be applied soon)
        is_spon_source = search('www\.spiegel\.de', r.text)
        contains_obfuscated_text = search(
            '<p[ ]+class=\"obfuscated\"[ ]*>', r.text)
        if is_spon_source and contains_obfuscated_text:
            b_util.log(
                'WARN: \'{}\' skipped because of missing deobfuscation of spiegel-plus content'.format(url))
            b_util.update_progressbar()
            return

        b_iotools.mkdirs(dir_key)

        f_handle = open(raw_fname, 'w')
        f_handle.write(r.text)
        f_handle.close()

        if b_iotools.file_exists(raw_fname):
            res_file = raw_fname
            res_size = b_iotools.get_file_size(raw_fname)
    b_util.update_progressbar()

urls = []
if args.l:
    urls = b_iotools.read_file_to_list(args.l)
    b_util.log('Read {} urls from link list'.format(len(urls)))
else:
    in_files = b_util.read_valid_inputfiles(args.i)
    for in_file in in_files:
        content = ''.join(b_iotools.read_file_to_list(in_file))
        entry = b_util.json_to_object(content)
        url = entry['link']
        urls.append(url)
    b_util.log('Read {} urls from feedparse files'.format(len(urls)))

b_util.setup_progressbar(len(urls))
pool = b_threading.ThreadPool(args.t)
for url in urls:
    pool.add_task(worker, url)
pool.wait_completion()
b_util.finish_progressbar()


def main():
    pass
