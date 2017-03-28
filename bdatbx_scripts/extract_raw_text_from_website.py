#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Extract main textual content from HTML to text files')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools, b_threading
import os
from bdatbx import b_util, b_parse

def worker(in_file):
    fulltext = '\n'.join(b_iotools.read_file_to_list(in_file))
    basename = os.path.basename(in_file)
    dirn = basename[:16]
    raw_fname = os.path.join(dirn, basename)
    if not b_iotools.file_exists(raw_fname):
        b_iotools.mkdirs(dirn)
        main_text = b_parse.extract_main_text_content(fulltext)
        f_handle = open(raw_fname, 'w')
        f_handle.write(main_text)
        f_handle.close()

        if b_iotools.file_exists(raw_fname):
            res_file = raw_fname
            res_size = b_iotools.get_file_size(raw_fname)
    b_util.update_progressbar()

in_files = b_util.read_valid_inputfiles(args.i)
b_util.setup_progressbar(len(in_files))
pool = b_threading.ThreadPool(args.t)
for in_file in in_files:
    pool.add_task(worker, in_file)
pool.wait_completion()
b_util.finish_progressbar()


def main():
    pass
