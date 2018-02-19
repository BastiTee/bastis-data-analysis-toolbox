#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reads a list of RSS feeds and writes out feedparse data or a URL list."""

import feedparser
from bptbx.b_iotools import read_file_to_list, mkdirs
from bptbx import b_cmdprs
from robota import r_util, r_const, r_mongo
from os import path

r_util.notify_start(__file__)

# ------------------------------------------------------------ CMD-LINE-PARSING
prs = b_cmdprs.TemplateArgumentParser(
    description='' +
    'Parse RSS feed URLs from file and store raw metadata')
prs.add_file_in()
prs.add_dir_out(ch_dir=True)
prs.add_mongo_collection(optional=True)
prs.add_bool('l', 'Only extract \'link\' tag.')
prs.add_verbose()
args = prs.parse_args()
col = r_mongo.get_client_for_collection(args.c, create=False)
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
        if col:
            r_mongo.add_doc(col, {
                '_id': fkey,
                r_const.DB_SOURCE_URI: link
            })
    r_util.update_progressbar()

r_util.finish_progressbar()


def main():
    """Void main entry."""
    pass
