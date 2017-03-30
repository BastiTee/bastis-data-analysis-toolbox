#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import langdetect
from bptbx.b_iotools import read_file_to_list
from bptbx import b_threading
from bdatbx import b_util
from os import path
from bdatbx.b_const import GLOBAL_INFILE_SUFFIX

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init(
    'Detect (or best-guess) the language of the given file\'s content')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_file_out(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_file_out(prs, args)
# -----------------------------------------------------------------------------

f_handle = open(args.o, 'w')

def worker(filepath):
    file_key, dir_key = b_util.get_key_from_url(filepath)
    raw_fname = path.join(dir_key, file_key + '.' + GLOBAL_INFILE_SUFFIX)
    in_text = ' '.join(read_file_to_list(filepath))
    #print (filepath)
    lang = langdetect.detect(in_text)
    f_handle.write('{} {} {}\n'.format(lang, file_key, filepath))
    b_util.update_progressbar()


in_files = b_util.read_valid_inputfiles(args.i)
b_util.setup_progressbar(len(in_files))
pool = b_threading.ThreadPool(1)
for in_file in in_files:
    pool.add_task(worker, in_file)
pool.wait_completion()
b_util.finish_progressbar()
f_handle.close()


def main():
    pass
