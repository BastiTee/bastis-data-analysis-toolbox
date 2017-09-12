#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reads a list of RSS feeds and writes out feedparse data or a URL list."""

import feedparser
from bptbx.b_iotools import read_file_to_list, mkdirs
from bptbx import b_cmdprs
from robota import r_util, r_const
from os import path

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
prs = b_cmdprs.init('Parse RSS feed URLs from file and store raw metadata')
b_cmdprs.add_file_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_bool(prs, '-l', 'Only extract \'link\' tag.')
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_file_in(prs, args.i)
b_cmdprs.check_dir_out_and_chdir(prs, args)
# -----------------------------------------------------------------------------

input_feeds = read_file_to_list(args.i)
r_util.setup_progressbar(len(input_feeds))
for input_feed in input_feeds:
    fp = feedparser.parse(input_feed)
    feed_key, _ = r_util.get_key_from_url(input_feed)

    for entry in fp['entries']:
        link = entry['link']
        fkey, dkey = r_util.get_key_from_url(link)
        target_dir = path.join(feed_key, dkey)
        target_file = path.join(target_dir, fkey + '.'
                                + r_const.GLOBAL_INFILE_SUFFIX)
        mkdirs(target_dir)
        out_file = open(target_file, 'w')
        out_file.write(r_util.object_to_json(entry))
        out_file.close()
    r_util.update_progressbar()

r_util.finish_progressbar()


def main():
    """Void main entry."""
    pass
