#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracts the raw main text content from an HTML page."""

from __future__ import with_statement
from bptbx import b_iotools, b_cmdprs
from robota import r_parse, r_const, r_mongo, r_util
from re import findall
import os

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = b_cmdprs.init('Extract main textual content from HTML to text files.')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------


def _worker(in_file, col=None, doc=None):
    try:
        fulltext = '\n'.join(b_iotools.read_file_to_list(in_file))
        basename = os.path.basename(in_file)
        dirn = basename[:16]
        raw_fname = os.path.join(dirn, basename)

        if not b_iotools.file_exists(raw_fname):
            r_mongo.set_null_safe(doc, r_const.DB_TE_RAWFILE, None)
            r_mongo.set_null_safe(doc, r_const.DB_TE_RAWFILESIZE, None)

            b_iotools.mkdirs(dirn)
            main_text = r_parse.extract_main_text_content(fulltext)
            if main_text:
                words = len(findall(r'[^\w]+', main_text))
                r_mongo.set_null_safe(doc, r_const.DB_TE_WC, words)

            f_handle = open(raw_fname, 'w')
            f_handle.write(main_text)
            f_handle.close()

            if b_iotools.file_exists(raw_fname):
                r_mongo.set_null_safe(
                    doc, r_const.DB_TE_RAWFILE, raw_fname)
                r_mongo.set_null_safe(
                    doc, r_const.DB_TE_RAWFILESIZE,
                    b_iotools.get_file_size(raw_fname))
    finally:
        r_mongo.replace_doc(col, doc)
        r_util.update_progressbar()


r_util.process_input_file_with_optional_collection(
    args, col, r_const.DB_DL_RAWFILE, _worker)


def main():
    """Void main entry."""
    pass
