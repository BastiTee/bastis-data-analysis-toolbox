#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement
from argparse import ArgumentParser
from bptbx import b_iotools, b_threading, b_web
import os
from threading import Lock
from re import sub, match
import hashlib
import shutil
import requests
import bs4
import progressbar


# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Dump main textual content of given URLs to text files.")
parser.add_argument("-i", metavar="<INPUT_FILE>",
                    help="Flat input text file with URLS.")
parser.add_argument("-t", metavar="<THREADS>",
                    help="Number of threads", default=10)
parser.add_argument("-f", action="store_true",
                    help="Run full data mode", default=False)
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
try:
    int(args.t)
except ValueError:
    show_help('Invalid number of threads.')
if int(args.t) <= 0:
    show_help('Invalid number of threads.')

print('-- using input file: {}'.format(args.i))
print('-- full-data mode: {}'.format(args.f))
print('-- threads used: {}'.format(args.t))
# --- CMD LINE PARSING END ----------------------------------------------------

# change to full parse folder
print('-- changed to: {}'.format(os.getcwd()))

# setup globals
sanity_limit = 50
input_lines = b_iotools.countlines(args.i)
if not args.f:
    input_lines = sanity_limit
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

# handle sanity mode
working_dir = '_full_parse'
if args.f == False:
    print("-- switching to sanity mode")
    working_dir = '_sanity'
    # cleanup last sanity run
    shutil.rmtree(working_dir, ignore_errors=True)

# setup folders
b_iotools.mkdirs(working_dir)
global_process_log_file = open(
    os.path.join(working_dir, 'process_log.csv'), 'w')
os.chdir(working_dir)
print('-- now in working dir {}'.format(os.getcwd()))


def fulltext_extraction(link):
    # permakey generation
    permakey = sub('[^a-zA-Z0-9_-]', '_', link)
    permakey = sub('^http[s]?_', '', permakey)
    permakey = sub('^_+', '', permakey)
    permakey = sub('_+$', '', permakey)[:75]
    chksum = hashlib.md5(link.encode('utf-8')).hexdigest()
    permakey = permakey + "_" + chksum
    # preparing output files
    dirn = 'fulltext/' + permakey[:16]
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
    if not args.f and int(idx) >= sanity_limit:
        break
    content = content.strip()
    pool.add_task(fulltext_extraction, content)
input_file.close()
pool.wait_completion()
if global_progressbar:
    global_progressbar.finish()
global_process_log_file.close()

def main():
    pass
