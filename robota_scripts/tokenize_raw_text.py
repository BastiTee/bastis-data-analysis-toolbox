#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Takes raw text content and writes out tokens."""

from __future__ import with_statement

import os
import nltk
from bptbx import b_iotools, b_threading, b_cmdprs
from robota import r_lists, r_mongo, r_const, r_util
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer

# ------------------------------------------------------------ CMD-LINE-PARSING
r_util.notify_start(__file__)
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


def _tokenize(text_lines):
    tokens = []
    for text_line in text_lines:
        tokens += nltk.tokenize.WordPunctTokenizer().tokenize(text_line)
    return tokens


def _remove_nonwords(tokens):
    from re import match
    filtered_tokens = []
    regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
    for token in tokens:
        if match(regex, token):
            filtered_tokens.append(token)
    return filtered_tokens


def _detect_language(tokens, doc=None):
    # check if we detected language before
    lang_db = r_mongo.get_key_nullsafe(doc, r_const.DB_LANG_AUTO)
    # if not try to decide between german and english
    if not lang_db:
        if (len(r_lists.intersect(tokens, SUPPORTED_LANGS['en']['sw'])) > len(
                r_lists.intersect(tokens, SUPPORTED_LANGS['de']['sw']))):
            lang_db = 'en'
        else:
            lang_db = 'de'
    try:
        return SUPPORTED_LANGS[lang_db]
    except KeyError:
        return SUPPORTED_LANGS['unk']


def _stem(tokens, stemmer, stem_2_source_dict):
    stemmed_tokens = []
    for token in tokens:
        stem = stemmer.stem(token)
        stemmed_tokens.append(stem)
        try:
            stem_2_source_dict[stem]
        except KeyError:  # stem never counted
            stem_2_source_dict[stem] = {}
        try:
            token_count = stem_2_source_dict[stem][token]
            stem_2_source_dict[stem][token] = token_count + 1
        except KeyError:  # token never counted
            stem_2_source_dict[stem][token] = 1

    return stemmed_tokens


def _stopword_removal(tokens, stopwords):
    filtered_tokens = []
    for token in tokens:
        if token not in stopwords:
            filtered_tokens.append(token)
    return filtered_tokens


def _write_dictionary_to_file(dictionary, stopwords, filename):
    sorted_dictionary = {}
    for dict_key in dictionary:  # for each stem in dictionary
        if dict_key in stopwords:
            continue  # don't
        dict_value = dictionary[dict_key]
        total_count = 0
        sorted_entries = []
        # sort stem variations by count
        for key, value in sorted(
            dict_value.items(), key=lambda item: (item[1], item[0]),
                reverse=True):
            sorted_entries.append(key)
            sorted_entries.append(value)
            total_count = total_count + value

        out_line = '{} {} {}\n'.format(
            dict_key, total_count, ' '.join([str(x) for x in sorted_entries]))
        sorted_dictionary[out_line] = total_count

    # sort dictionary by stem count and write to file
    ofile = open(filename, 'w')
    for key, value in sorted(
            sorted_dictionary.items(), key=lambda item: (
            item[1], item[0]), reverse=True):
        ofile.write(key)
    ofile.close()


def _extend_stopwords_with_manual_list(stopwords, lang):
    path = r_util.get_resource_filepath('stopwords_{}_add.txt'.format(lang))
    new_stopwords = b_iotools.read_file_to_list(path)
    r_util.log('Will add {} stopwords from {} to {} stopword list'.format(
        len(new_stopwords), path, lang))
    stopwords += new_stopwords
    return stopwords


def _worker(in_file, col=None, doc=None):
    try:
        # when using mongo, check if word count is relevant
        if doc is not None:
            wc = r_mongo.get_key_nullsafe(doc, r_const.DB_TE_WC)
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
        tokens = _tokenize(text_lines)
        tokens = _remove_nonwords(tokens)
        lang_kit = _detect_language(tokens, doc)
        tokens = _stem(tokens, lang_kit['stemmer'], lang_kit['s2s'])
        tokens = _stopword_removal(tokens, lang_kit['sw'])
        r_mongo.set_null_safe(doc, r_const.DB_TOK_WC, len(tokens))
        r_mongo.set_null_safe(doc, r_const.DB_TOK_TOKENS, tokens)
        # ------------------------------------------------
        b_iotools.write_list_to_file(tokens, raw_fname)
        if b_iotools.file_exists(raw_fname):
            r_mongo.set_null_safe(doc, r_const.DB_TOK_RAWFILE, raw_fname)
            r_mongo.set_null_safe(doc, r_const.DB_TOK_RAWFILESIZE,
                                  b_iotools.get_file_size(raw_fname))
        # ------------------------------------------------
    finally:
        r_mongo.replace_doc(col, doc)
        r_util.update_progressbar()


# setup language tools
if args.n:
    nltk.data.path.append(args.n)
    r_util.log('added nltk path {}'.format(args.n))

SUPPORTED_LANGS = {
    'de': {'name': 'german'},
    'en': {'name': 'english'},
    'es': {'name': 'spanish'},
    'unk': {'name': 'unknown'}
}
for iso, lang_kit in SUPPORTED_LANGS.items():
    if iso == 'unk':
        continue
    lang = lang_kit['name']
    lang_kit['stemmer'] = SnowballStemmer(lang, ignore_stopwords=False)
    lang_kit['sw'] = (
        [lang_kit['stemmer'].stem(sw)
         for sw in _extend_stopwords_with_manual_list(
            stopwords.words(lang), lang)])
    lang_kit['s2s'] = {}
    r_util.log('-- finished setup for language {}/{}'.format(iso, lang))
SUPPORTED_LANGS['unk']['stemmer'] = SUPPORTED_LANGS['en']['stemmer']
SUPPORTED_LANGS['unk']['sw'] = SUPPORTED_LANGS['en']['sw']
SUPPORTED_LANGS['unk']['s2s'] = {}

pool = b_threading.ThreadPool(args.t)
if args.i and not col:
    in_files = r_util.read_valid_inputfiles(args.i)
    r_util.setup_progressbar(len(in_files))
    for in_file in in_files:
        _worker(in_file)
elif col:
    r_util.setup_progressbar(r_mongo.get_collection_size(col))
    cursor = r_mongo.get_snapshot_cursor(col, no_cursor_timeout=True)
    for doc in cursor:
        raw_text = r_mongo.get_key_nullsafe(doc, r_const.DB_TE_RAWFILE)
        if raw_text:
            in_file = os.path.join(args.i, raw_text)
            pool.add_task(_worker, in_file, col, doc)
    cursor.close()
pool.wait_completion()
r_util.finish_progressbar()

# write out data points
for kit in list(SUPPORTED_LANGS.values()):
    ofile = 'token_dict_{}.txt'.format(kit['name'])
    b_iotools.remove_silent(ofile)
    _write_dictionary_to_file(kit['s2s'], kit['sw'], ofile)


def main():
    """Void main entry."""
    pass
