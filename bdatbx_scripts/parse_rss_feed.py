#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from re import sub
from bptbx import b_iotools
from argparse import ArgumentParser
import feedparser

parser = ArgumentParser(
    description="Parse RSS feed.")
parser.add_argument("-i", metavar='FEED', help="RSS feed URL")
parser.add_argument("-o", metavar='OUTPUT', help="Output data file")
parser.add_argument("-l", action="store_true",
                    help="Only extract 'link' tag.", default=False)
parser.add_argument("-v", action="store_true",
                    help="Verbose output.", default=False)
args = parser.parse_args()


def show_help(message):
    print(message)
    parser.print_help()
    exit(1)

if args.i is None:
    show_help("No feed URL provided.")
if args.o is None:
    show_help("No output file provided.")
if b_iotools.file_exists(args.o):
    show_help("Output file already exists.")

fp = feedparser.parse(args.i)
ofile = open(args.o, 'w')

if args.l is True:
    for entry in fp['entries']:
        output = entry['link']
        if args.v:
            print(output)
        ofile.write(output + '\n')
    ofile.close()
    exit(0)

ofile.close()
