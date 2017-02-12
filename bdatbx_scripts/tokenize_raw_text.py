#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Tokenize raw text files')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_opt_dir_in(prs, '-n', 'Additional NLTK data directory')
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
args.n = b_cmdprs.check_opt_dir_in(prs, args.n)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
# -----------------------------------------------------------------------------

import os
import nltk
from bptbx import b_iotools, b_threading
from bdatbx import b_lists, b_util
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


def tokenize(text_lines):
    tokens = []
    for text_line in text_lines:
        tokens += nltk.tokenize.WordPunctTokenizer().tokenize(text_line)
    return tokens


def remove_nonwords(tokens):
    from re import match
    filtered_tokens = []
    regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
    for token in tokens:
        if match(regex, token):
            filtered_tokens.append(token)
    return filtered_tokens


def guess_language(tokens):
    if (len(b_lists.intersect(tokens, sw_en)) > len(
            b_lists.intersect(tokens, sw_de))):
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


def stem(tokens, stemmer, stem_2_source_dict):
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


def stopword_removal(tokens, stopwords):
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


def worker(worker_set):
    if not in_file or not b_iotools.file_exists(in_file):
        print('   + warning: {} not found.'.format(in_file))
        update_global_process(worker_set)
        return
    basename = os.path.basename(in_file)
    dirn = basename[:16]
    b_iotools.mkdirs(dirn)
    out_file = os.path.join(dirn, basename)
    if b_iotools.file_exists(out_file):
        b_util.update_progressbar()
        return
    # ------------------------------------------------
    text_lines = b_iotools.read_file_to_list(in_file, True)
    tokens = tokenize(text_lines)
    tokens = remove_nonwords(tokens)
    total_words = len(tokens)
    language, stopwords, stemmer, s2s_dict = guess_language(tokens)
    tokens = stem(tokens, stemmer, s2s_dict)
    tokens = stopword_removal(tokens, stopwords)
    # ------------------------------------------------
    b_iotools.mkdirs(os.path.dirname(out_file))
    b_iotools.write_list_to_file(tokens, out_file)
    # ------------------------------------------------
    # save newly gathered information
    b_util.update_progressbar()


# setup NLTK
if args.n:
    nltk.data.path.append(args.n)
    print('-- added nltk path {}'.format(args.n))
stem_en = SnowballStemmer('english', ignore_stopwords=False)
stem_de = SnowballStemmer('german', ignore_stopwords=False)
sw_en = [stem_en.stem(sw) for sw in stopwords.words('english')]
sw_de = [stem_de.stem(sw) for sw in stopwords.words('german')]
stem_2_source_dict_en = {}
stem_2_source_dict_de = {}

# run processing
in_files = b_iotools.findfiles(args.i, '.*\\.txt')
b_util.setup_progressbar(len(in_files))
for in_file in in_files:
    worker(in_file)
b_util.finish_progressbar()

# write out data points
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
