#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extracts the raw main text content from an HTML page."""

from __future__ import with_statement
from bptbx import b_iotools, b_cmdprs
from robota import r_const, r_mongo, r_util, r_date_extractor

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = b_cmdprs.init('Extract main textual content from HTML to text files.')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_bool(prs, '-f', 'Only print out URLs with no date extracted.')
b_cmdprs.add_file_out(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_file_out(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------


def _worker(in_file, col=None, doc=None):
    try:
        raw_html = '\n'.join(b_iotools.read_file_to_list(in_file))
        url = r_mongo.get_key_nullsafe(doc, r_const.DB_SOURCE_URI)
        if not url:
            url = ''
        date, hint = r_date_extractor.extract_article_pubdate(url, raw_html)

        epoch = int(date.strftime('%s')) if date else None

        if not hint:
            err_handle.write('{}\n'.format(url))
        else:
            out_handle.write('{};{};{};{}\n'.format(date, epoch, hint, url))

        r_mongo.set_null_safe(doc, r_const.DB_DATE_HR, date)
        r_mongo.set_null_safe(doc, r_const.DB_DATE_EP, epoch)
        r_mongo.set_null_safe(doc, r_const.DB_DATE_HINT, hint)

    finally:
        r_mongo.replace_doc(col, doc)
        r_util.update_progressbar()


out_handle = open(args.o, 'w')
err_handle = open(args.o + '.failed', 'w')
r_util.process_input_file_with_optional_collection(
    args, col, r_const.DB_DL_RAWFILE, _worker, threads=1,
    query={r_const.DB_DL_RAWFILE: {'$ne': None}})
out_handle.close()
err_handle.close()


def main():
    """Void main entry."""
    pass
