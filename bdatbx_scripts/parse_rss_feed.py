#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs, b_util
b_util.notify_start(__file__)
prs = b_cmdprs.init('Parse RSS feed URLs from file and store raw metadata')
b_cmdprs.add_file_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_bool(prs, '-l', 'Only extract \'link\' tag.')
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_file_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
# -----------------------------------------------------------------------------

import feedparser
from bptbx.b_iotools import read_file_to_list, mkdirs
from bdatbx.b_const import GLOBAL_INFILE_SUFFIX
from os import path

input_feeds = read_file_to_list(args.i)
b_util.setup_progressbar(len(input_feeds))
for input_feed in input_feeds:
    fp = feedparser.parse(input_feed)
    feed_key, _ = b_util.get_key_from_url(input_feed)

    for entry in fp['entries']:
        link = entry['link']
        fkey, dkey = b_util.get_key_from_url(link)
        target_dir = path.join(feed_key, dkey)
        target_file = path.join(target_dir, fkey + '.' + GLOBAL_INFILE_SUFFIX)
        mkdirs(target_dir)
        out_file = open(target_file, 'w')
        out_file.write(b_util.object_to_json(entry))
        out_file.close()

    b_util.update_progressbar()

b_util.finish_progressbar()

def main():
    pass
