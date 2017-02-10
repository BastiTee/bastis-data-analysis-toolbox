#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
import feedparser

# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Parse RSS feed.")
parser.add_argument("-i", help="Feed address")
parser.add_argument("-l", action="store_true",
                    help="Only print links.", default=False)
args = parser.parse_args()


def show_help(message):
    print(message)
    parser.print_help()
    exit(1)

if args.i is None:
    show_help("No feed URL provided.")


fp = feedparser.parse(args.i)

if args.l is True:
    for entry in fp['entries']:
        print(entry['link'])
    exit(0)

print('-- more soon --')


# http://www.spiegel.de/index.rss
