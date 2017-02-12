#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Dump website content of given URLs to text files')
b_cmdprs.add_file_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_file_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools, b_threading
from os import path
import requests
from bdatbx import b_util


def worker(link):
    file_key, dir_key = b_util.get_key_from_url(link)
    raw_fname = path.join(dir_key, file_key + '.txt')

    if not b_iotools.file_exists(raw_fname):
        try:
            r = requests.get(link, timeout=10)
            res_code = r.status_code
        except Exception as e:
            print('   + ERROR for \'{}\': {}'.format(link, e))
            b_util.update_progressbar()
            return
        if res_code is not 200:
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

input_file = open(args.i)
item_count = b_iotools.countlines(args.i)
b_util.setup_progressbar(item_count)
pool = b_threading.ThreadPool(args.t)
for idx, content in enumerate(input_file):
    content = content.strip()
    pool.add_task(worker, content)
input_file.close()
pool.wait_completion()
b_util.finish_progressbar()


def main():
    pass
