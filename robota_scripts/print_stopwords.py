#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Print all known stopwords for a language."""

from robota import r_preproc
import os
import nltk
from bptbx import b_iotools, b_threading, b_cmdprs
from robota import r_util, r_mongo, r_const, r_textrank

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = b_cmdprs.init('Print stopwords for a given language.')
b_cmdprs.add_opt_dir_in(prs, '-n', 'Additional NLTK data directory')
b_cmdprs.add_option(prs, '-l', 'Language (Mandatory)')
args = prs.parse_args()
args.n = b_cmdprs.check_opt_dir_in(prs, args.n)
b_cmdprs.check_option(prs, args.l)
# -----------------------------------------------------------------------------
if args.n:
    nltk.data.path.append(args.n)
    r_util.log('added nltk path {}'.format(args.n))

stopwords = r_preproc.get_stopwords_for_language(args.l)
[ print(stopword) for stopword in stopwords ]