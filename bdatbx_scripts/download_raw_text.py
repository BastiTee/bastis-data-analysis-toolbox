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
                    help="Flat input text file with URLS.")
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
    show_help('No input file set.')
if not b_iotools.file_exists(args.i):
    show_help('Input file does not exist.')
args.i = os.path.abspath(args.i)
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

print('-- using input file: {}'.format(args.i))
print('-- threads used: {}'.format(args.t))
# --- CMD LINE PARSING END ----------------------------------------------------

# change to full parse folder
print('-- changed to: {}'.format(os.getcwd()))

# setup globals
input_lines = b_iotools.countlines(args.i)
global_progressbar = None
global_progress = 0
global_progressbar_lock = Lock()
global_logfile_lock = Lock()


def write_to_process_log(
        link, permakey, res_code='', out_file='', out_file_size=''):
    global global_process_log_file
    with global_logfile_lock:
        global_process_log_file.write('{};\"{}\";{};\"{}\";{}\n'.format(
            permakey, link, res_code, out_file, out_file_size))


def update_global_process():
    with global_progressbar_lock:
        global global_progress
        global global_progressbar
        if not global_progressbar:
            return
        global_progress += 1
        global_progressbar.update(global_progress)

# setup folders
global_process_log_file = open(
    os.path.join(working_dir, 'process_log.csv'), 'w')

def fulltext_extraction(link):
    # permakey generation
    permakey = b_util.get_key_from_url(link)
    # preparing output files
    dirn = permakey[:16]
    raw_fname = os.path.join(dirn, permakey + '.txt')
    if not b_iotools.file_exists(raw_fname):
        try:
            r = requests.get(link, timeout=10)
            res_code = r.status_code
        except Exception as e:
            print('   + ERROR for \'{}\': {}'.format(link, e))
            write_to_process_log(link, permakey, 'ERR')
            update_global_process()
            return
        if res_code is not 200:
            write_to_process_log(link, permakey, res_code)
            update_global_process()
            return
        b_iotools.mkdirs(dirn)
        main_text = b_web.extract_main_text_content(r.text)
        f_handle = open(raw_fname, 'w')
        f_handle.write(main_text)
        f_handle.close()

        if b_iotools.file_exists(raw_fname):
            if not global_progressbar:
                print('   + {}'.format(raw_fname))
            res_file = raw_fname
            res_size = b_iotools.get_file_size(raw_fname)
            write_to_process_log(link, permakey, res_code, res_file, res_size)
        else:
            write_to_process_log(link, permakey, res_code)
    update_global_process()

input_file = open(args.i)
pool = b_threading.ThreadPool(int(args.t))
global_progressbar = progressbar.ProgressBar(max_value=input_lines)
for idx, content in enumerate(input_file):
    content = content.strip()
    pool.add_task(fulltext_extraction, content)
input_file.close()
pool.wait_completion()
if global_progressbar:
    global_progressbar.finish()
global_process_log_file.close()

def main():
    pass
