#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import csv
from argparse import ArgumentParser
from bptbx import b_iotools

# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Gather some text statistics.")
parser.add_argument("-i", metavar="INPUT",
                    help="Input directory containing raw fulltext files.")
parser.add_argument("-o", metavar="OUTPUT",
                    help="Output directory.")
args = parser.parse_args()


def show_help(message):
    print(message)
    parser.print_help()
    exit(1)

if not args.i:
    show_help('No input directory set.')
if not os.path.isdir(args.i):
    show_help("Input directory does not exist.")
input_dir = os.path.abspath(args.i)

if not args.o:
    show_help('No output directory set.')
if not os.path.isdir(args.o):
    show_help("Output directory does not exist.")
working_dir = os.path.abspath(args.o)
os.chdir(working_dir)
print('-- now in working dir {}'.format(os.getcwd()))

# --- CMD LINE PARSING END ----------------------------------------------------

global_log_in=os.path.join(input_dir, 'process_log.csv')
global_log_out=os.path.join(working_dir, 'process_log.csv')

plain_datasets=[]
with open(global_log_in, 'r') as csvfile:
    datasets=csv.reader(csvfile, delimiter = ';', quotechar = '"')
    for dataset in datasets:
        plain_datasets.append(dataset)
csvfile.close()

# CURRENT FORMAT:
#  [0] - Generated permakey
#  [1] - Source permalink
#  [2] - HTTP response code
#  [3] - Path to downloaded raw text data
#  [4] - Raw text data file size in bytes
#  [5] - Estimated content language
#  [6] - Total number of tokens
#  [7] - Total number of stemmed and stopword-cleared tokens
#  [8] - Path to tokenized text data

total_usable=0
total_de=0
total_en=0
min_tokens=None
max_tokens=None
total_tokens=None
avg_tokens=None
for d in plain_datasets:
    if d[2] != '200' or not d[7] or not int(d[7]) > 10:
        continue
    total_usable += 1
    if d[5] == 'en':
        total_en += 1
    else:
        total_de += 1
    if total_usable == 1:
        min_tokens=max_tokens=avg_tokens=total_tokens=int(d[7])
    else:
        min_tokens=min(min_tokens, int(d[7]))
        max_tokens=max(max_tokens, int(d[7]))
        total_tokens += int(d[7])
        avg_tokens=total_tokens / total_usable


print('-- datasets')
print('   + total:    {}'.format(len(plain_datasets)))
print('   + usable:   {}'.format(total_usable))
print('   + german:   {}'.format(total_de))
print('   + english:  {}'.format(total_en))
print('-- tokens')
print('   + total:    {}'.format(total_tokens))
print('   + min:      {}'.format(min_tokens))
print('   + max:      {}'.format(max_tokens))
print('   + avg:      {}'.format(int(avg_tokens)))

def main():
    pass
