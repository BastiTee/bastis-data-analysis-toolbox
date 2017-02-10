#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement
from argparse import ArgumentParser
from bptbx import b_iotools, b_threading, b_web
import os
from threading import Lock
from re import sub, match
import shutil
import requests
import bs4
import progressbar
from bdatbx import b_util


# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Dump main textual content of given URLs to text files.")
parser.add_argument("-i", metavar="INPUT",
                    help="Input directory containing HTML dumps.")
parser.add_argument("-o", metavar="OUTPUT",
                    help="Output directory.")
parser.add_argument("-t", metavar="THREADS",
                    help="Number of threads", default=10)
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

try:
    int(args.t)
except ValueError:
    show_help('Invalid number of threads.')
if int(args.t) <= 0:
    show_help('Invalid number of threads.')

print('-- threads used: {}'.format(args.t))
# --- CMD LINE PARSING END ----------------------------------------------------

# change to full parse folder
print('-- changed to: {}'.format(os.getcwd()))

# setup globals
in_files = b_iotools.findfiles(input_dir, '.*\\.txt')
input_lines = len(in_files)
global_progressbar = None
global_progress = 0
global_progressbar_lock = Lock()


def write_to_process_log(
        link, permakey, res_code='', out_file='', out_file_size=''):
    pass

def update_global_process():
    with global_progressbar_lock:
        global global_progress
        global global_progressbar
        if not global_progressbar:
            return
        global_progress += 1
        global_progressbar.update(global_progress)

def fulltext_extraction(in_file):
    fulltext = '\n'.join(b_iotools.read_file_to_list(in_file))
    basename = os.path.basename(in_file)
    dirn = basename[:16]
    raw_fname = os.path.join(dirn, basename)
    if not b_iotools.file_exists(raw_fname):
        b_iotools.mkdirs(dirn)
        main_text = b_web.extract_main_text_content(fulltext)
        f_handle = open(raw_fname, 'w')
        f_handle.write(main_text)
        f_handle.close()

        if b_iotools.file_exists(raw_fname):
            if not global_progressbar:
                print('   + {}'.format(raw_fname))
            res_file = raw_fname
            res_size = b_iotools.get_file_size(raw_fname)
            write_to_process_log(basename, '-')
        else:
            write_to_process_log(basename, '-')
    update_global_process()

pool = b_threading.ThreadPool(int(args.t))
global_progressbar = progressbar.ProgressBar(max_value=input_lines)
for in_file in in_files:
    pool.add_task(fulltext_extraction, in_file)
pool.wait_completion()
if global_progressbar:
    global_progressbar.finish()

def main():
    pass
