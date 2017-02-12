#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Parse RSS feed URLs from file and store raw metadata')
b_cmdprs.add_file_in(prs)
b_cmdprs.add_file_out(prs)
b_cmdprs.add_bool(prs, '-l', 'Only extract \'link\' tag.')
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_file_in(prs, args)
b_cmdprs.check_file_out(prs, args)
# -----------------------------------------------------------------------------

import feedparser
from bptbx.b_iotools import read_file_to_list

input_feeds = read_file_to_list(args.i)
out_file = open(args.o, 'w')
for input_feed in input_feeds:
    fp = feedparser.parse(input_feed)

    for entry in fp['entries']:
        if args.l is True:
            output = entry['link']
        else:
            output = str(entry)

        if args.v:
            print(output)
        out_file.write(output + '\n')

out_file.close()


def main():
    pass
