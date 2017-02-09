#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import with_statement
import os
import csv
import re
import progressbar
import nltk
import time
import shutil
from threading import Lock
from argparse import ArgumentParser

from bptbx import b_iotools, b_math, b_threading
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Preprocess main textual content previously downloaded.")
parser.add_argument("-t", metavar="<THREADS>",
                    help="Number of threads", default=10)
parser.add_argument("-f", action="store_true",
                    help="Run full data mode", default=False)
args = parser.parse_args()


def show_help(message):
    print(message)
    parser.print_help()
    exit(1)

try:
    int(args.t)
except ValueError:
    show_help('Invalid number of threads.')
if int(args.t) <= 0:
    show_help('Invalid number of threads.')
# setup nltk
file_limit = 250
if args.f:
    file_limit = 0

print('-- full-data mode: {}'.format(args.f))
print('-- threads used: {}'.format(args.t))

# --- CMD LINE PARSING END ----------------------------------------------------

# setup globals
global_progressbar = None
global_progress = 0
global_lock = Lock()
global_plain_datasets_ext = []


def update_global_process(dataset):
    with global_lock:
        global global_plain_datasets_ext
        global_plain_datasets_ext.append(dataset)

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

# setup environment
try:
    os.chdir(working_dir)
except FileNotFoundError:
    show_help('You need to run the download-step first.')
print('-- changed to: {}'.format(os.getcwd()))


def extend_stopwords(language, stopwords):
    source = 'stopwords_{}_add.txt'.format(language)
    add_stopwords = []
    if b_iotools.file_exists(os.path.join('..', 'resource', source)):
        print('-- attaching manual set of stopwords from {}'.format(source))
        add_stopwords = b_iotools.read_file_to_list(os.path.join('..', source))
    stopwords = stopwords + add_stopwords
    stopwords = list(filter(None, set(stopwords)))
    return stopwords

nltk.data.path.append(os.path.join('..', 'nltk-data'))
stem_en = SnowballStemmer('english', ignore_stopwords=False)
stem_de = SnowballStemmer('german', ignore_stopwords=False)
sw_en = [stem_en.stem(sw) for sw in extend_stopwords(
    'en', stopwords.words('english'))]
sw_de = [stem_de.stem(sw) for sw in extend_stopwords(
    'de', stopwords.words('german'))]
stem_2_source_dict_en = {}
stem_2_source_dict_de = {}


def preprocess_tokenize(text_lines):
    tokens = []
    for text_line in text_lines:
        tokens += nltk.tokenize.WordPunctTokenizer().tokenize(text_line)
    return tokens


def preprocess_remove_nonwords(tokens):
    filtered_tokens = []
    regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
    for token in tokens:
        if re.match(regex, token):
            filtered_tokens.append(token)
    return filtered_tokens


def preprocess_guess_language(tokens):
    if (len(b_math.intersect(tokens, sw_en)) > len(
            b_math.intersect(tokens, sw_de))):
        language = 'en'
        stopwords = sw_en
        stemmer = stem_en
        s2sdict = stem_2_source_dict_en
    else:
        language = 'de'
        stopwords = sw_de
        stemmer = stem_de
        s2sdict = stem_2_source_dict_de

    return language, stopwords, stemmer, s2sdict


def preprocess_stem(tokens, stemmer, stem_2_source_dict):
    stemmed_tokens = []
    for token in tokens:
        stem = stemmer.stem(token)
        stemmed_tokens.append(stem)
        try:
            dict_entry = stem_2_source_dict[stem]
        except KeyError:  # stem never counted
            stem_2_source_dict[stem] = {}
        try:
            token_count = stem_2_source_dict[stem][token]
            stem_2_source_dict[stem][token] = token_count + 1
        except KeyError:  # token never counted
            stem_2_source_dict[stem][token] = 1

    return stemmed_tokens


def preprocess_stopword_removal(tokens, stopwords):
    filtered_tokens = []
    for token in tokens:
        if not token in stopwords:
            filtered_tokens.append(token)
    return filtered_tokens


def write_dictionary_to_file(dictionary, stopwords, filename):

    sorted_dictionary = {}
    for dict_key in dictionary:  # for each stem in dictionary
        if dict_key in stopwords:
            continue  # don't handle stop words
        dict_value = dictionary[dict_key]
        total_count = 0
        sorted_entries = []
        # sort stem variations by count
        for key, value in sorted(
                dict_value.items(), key=lambda item: (item[1], item[0]), reverse=True):
            sorted_entries.append(key)
            sorted_entries.append(value)
            total_count = total_count + value

        out_line = '{} {} {}\n'.format(
            dict_key, total_count, ' '.join([str(x) for x in sorted_entries]))
        sorted_dictionary[out_line] = total_count

    # sort dictionary by stem count and write to file
    ofile = open(filename, 'w')
    for key, value in sorted(
            sorted_dictionary.items(), key=lambda item: (item[1], item[0]), reverse=True):
        ofile.write(key)
    ofile.close()


def preprocess_worker(worker_set):
    if not worker_set[3] or not b_iotools.file_exists(worker_set[3]):
        update_global_process(worker_set)
        return
    in_file = worker_set[3]
    out_file = re.sub('^fulltext', 'preproc', in_file)
    if b_iotools.file_exists(out_file):
        update_global_process(worker_set)
        return
    if not global_progressbar:
        print('   + {}'.format(in_file))
    # ------------------------------------------------
    text_lines = b_iotools.read_file_to_list(in_file, True)
    tokens = preprocess_tokenize(text_lines)
    tokens = preprocess_remove_nonwords(tokens)
    total_words = len(tokens)
    language, stopwords, stemmer, s2s_dict = preprocess_guess_language(tokens)
    tokens = preprocess_stem(tokens, stemmer, s2s_dict)
    tokens = preprocess_stopword_removal(tokens, stopwords)
    # ------------------------------------------------
    b_iotools.mkdirs(os.path.dirname(out_file))
    b_iotools.write_list_to_file(tokens, out_file)
    # ------------------------------------------------
    # save newly gathered information
    while len(worker_set) < 9:
        worker_set.append('')
    worker_set[5] = language
    worker_set[6] = total_words
    worker_set[7] = len(tokens)
    worker_set[8] = out_file
    update_global_process(worker_set)

# main processing loop
global_process_log_file = os.path.join(os.getcwd(), 'process_log.csv')
plain_datasets = []
with open(global_process_log_file, 'r') as csvfile:
    datasets = csv.reader(csvfile, delimiter=';', quotechar='"')
    for dataset in datasets:
        plain_datasets.append(dataset)

global_progressbar = progressbar.ProgressBar(max_value=len(plain_datasets))
for plain_dataset in plain_datasets:
    preprocess_worker(plain_dataset)
if global_progressbar:
    global_progressbar.finish()
csvfile.close()


print("-- done preprocessing.")
print("-- writing new data points.")
os.remove(global_process_log_file)
with open(global_process_log_file, 'w') as csvfile:
    log_writer = csv.writer(csvfile, delimiter=';',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for plain_dataset in global_plain_datasets_ext:
        log_writer.writerow(plain_dataset)
csvfile.close()

print("-- writing token dictionaries.")
for lang in ['de', 'en']:
    label = 'dictionary_{}.txt'.format(lang)
    if b_iotools.file_exists(label):
        os.remove(label)
    lang_dict = stem_2_source_dict_de
    stopwords = sw_de
    if lang == 'en':
        lang_dict = stem_2_source_dict_en
        stopwords = sw_en
    write_dictionary_to_file(lang_dict, stopwords, label)

def main():
    pass
