#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import with_statement

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Tokenize raw text files')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_mongo_collection(prs)
b_cmdprs.add_opt_dir_in(prs, '-n', 'Additional NLTK data directory')
b_cmdprs.add_max_threads(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
args.n = b_cmdprs.check_opt_dir_in(prs, args.n)
b_cmdprs.check_dir_out_and_chdir(prs, args)
b_cmdprs.check_max_threads(prs, args)
col = b_cmdprs.check_mongo_collection(prs, args)
# -----------------------------------------------------------------------------

import os
import nltk
from bptbx import b_iotools, b_threading
from bdatbx import b_lists, b_util, b_mongo, b_const
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

SUPPORTED_LANGS = {
    'de': 'german',
    'en': 'english',
    'unk': 'unknown'
}

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


def detect_language(tokens, doc=None):
    # check if we detected language before
    lang_db = b_mongo.get_key_nullsafe(doc, b_const.DB_LANG_AUTO)
    # if not try to decide between german and english
    if not lang_db:
        if (len(b_lists.intersect(tokens, sw_en)) > len(
                b_lists.intersect(tokens, sw_de))):
            lang_db = 'en'
        else:
            lang_db = 'de'
    if lang_db == 'de':
        return 'de', sw_de, stem_de, stem_2_source_dict_de
    elif lang_db == 'en':
        return 'en', sw_en, stem_en, stem_2_source_dict_en
    else:
        return 'unk', sw_en, stem_en, stem_2_source_dict_unk


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


def write_dictionary_to_file(dictionary, filename):
    sorted_dictionary = {}
    for dict_key in dictionary:  # for each stem in dictionary
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


def extend_stopwords_with_manual_list(stopwords, lang):
    path = b_util.load_resource_file('stopwords_{}_add.txt'.format(lang))
    new_stopwords = b_iotools.read_file_to_list(path)
    b_util.log('Will add {} stopwords from {} to {} stopword list'.format(
        len(new_stopwords), path, lang))
    stopwords += new_stopwords
    return stopwords


def worker(in_file, col=None, doc=None):

    try:
        # when using mongo, check if word count is relevant
        if doc is not None:
            wc = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_WC)
            if wc is None or wc < 1:
                return
        # check if input file is present
        if not in_file or not b_iotools.file_exists(in_file):
            return
        # generate output paths
        basename = os.path.basename(in_file)
        dirn = basename[:16]
        raw_fname = os.path.join(dirn, basename)
        if b_iotools.file_exists(raw_fname):
            return
        b_iotools.mkdirs(dirn)
        # ------------------------------------------------
        text_lines = b_iotools.read_file_to_list(in_file, True)
        tokens = tokenize(text_lines)
        tokens = remove_nonwords(tokens)
        language, stopwords, stemmer, s2s_dict = detect_language(tokens, doc)
        tokens = stem(tokens, stemmer, s2s_dict)
        tokens = stopword_removal(tokens, stopwords)
        b_mongo.set_null_safe(doc, b_const.DB_TOK_WC, len(tokens))
        b_mongo.set_null_safe(doc, b_const.DB_TOK_TOKENS, tokens)
        # ------------------------------------------------
        b_iotools.write_list_to_file(tokens, raw_fname)
        if b_iotools.file_exists(raw_fname):
            b_mongo.set_null_safe(doc, b_const.DB_TOK_RAWFILE, raw_fname)
            b_mongo.set_null_safe(doc, b_const.DB_TOK_RAWFILESIZE,
            b_iotools.get_file_size(raw_fname))
        # ------------------------------------------------
    finally:
        b_mongo.replace_doc(col, doc)
        b_util.update_progressbar()


# setup NLTK
if args.n:
    nltk.data.path.append(args.n)
    b_util.log('added nltk path {}'.format(args.n))
stem_en = SnowballStemmer('english', ignore_stopwords=False)
stem_de = SnowballStemmer('german', ignore_stopwords=False)
sw_en = [stem_en.stem(sw) for sw in extend_stopwords_with_manual_list(
    stopwords.words('english'), 'english')]
sw_de = [stem_de.stem(sw) for sw in extend_stopwords_with_manual_list(
    stopwords.words('german'), 'german')]
stem_2_source_dict_de = {}
stem_2_source_dict_en = {}
stem_2_source_dict_unk = {}

pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = b_util.read_valid_inputfiles(args.i)
    b_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        worker(in_file)
elif col:
    b_util.setup_progressbar(b_mongo.get_collection_size(col))
    cursor = b_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    i = 0
    for doc in cursor:
        raw_text = b_mongo.get_key_nullsafe(doc, b_const.DB_TE_RAWFILE)
        if raw_text:
            in_file = os.path.join(args.i, raw_text)
            pool.add_task(worker, in_file, col, doc)
        i += 1
    cursor.close()
    b_util.log('Cursor closed. Added {} jobs to job queue.'.format(i))
pool.wait_completion()
b_util.finish_progressbar()

# write out data points
for lang in list(SUPPORTED_LANGS.keys()):
    ofile = 'token_dictionary_{}.txt'.format(lang)
    b_iotools.remove_silent(ofile)
    if lang == 'de':
        write_dictionary_to_file(stem_2_source_dict_de, ofile)
    elif lang == 'en':
        write_dictionary_to_file(stem_2_source_dict_en, ofile)
    else:
        write_dictionary_to_file(stem_2_source_dict_unk, ofile)

def main():
    pass
