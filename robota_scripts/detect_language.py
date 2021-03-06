#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatically detect the language of the provided text samples."""

import langdetect
from bptbx import b_iotools, b_cmdprs
from os import path
from re import findall
from robota import r_const, r_util, r_mongo

r_util.notify_start(__file__)

# ------------------------------------------------------------ CMD-LINE-PARSING
prs = b_cmdprs.TemplateArgumentParser(
    description='' +
    'Detect (or best-guess) the language of the given file\'s content')
prs.add_dir_in()
prs.add_mongo_collection(optional=True)
prs.add_file_out()
args = prs.parse_args()
col = r_mongo.get_client_for_collection(args.c, create=False)
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
r_util.process_input_file_with_optional_collection(
    args, col, r_const.DB_TE_RAWFILE, _worker, threads=1)
f_handle.close()


def main():
    """Void main entry."""
    pass
