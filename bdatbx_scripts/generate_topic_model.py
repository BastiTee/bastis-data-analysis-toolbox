#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from argparse import ArgumentParser
from gensim import corpora, models
import gensim.models.word2vec
from bptbx import b_iotools

# --- CMD LINE PARSING BEGIN --------------------------------------------------
parser = ArgumentParser(
    description="Generate LDA topic models.")
parser.add_argument("-f", action="store_true",
                    help="Run full data mode", default=False)
args = parser.parse_args()


def show_help(message):
    print(message)
    parser.print_help()
    exit(1)
file_limit = 250
if args.f:
    file_limit = 0

print('-- full-data mode: {}'.format(args.f))

# --- CMD LINE PARSING END ----------------------------------------------------
working_dir = '_full_parse'
lda_topics = 5
lda_passes = 2
if args.f == False:
    print("-- switching to sanity mode")
    working_dir = '_sanity'

try:
    os.chdir(working_dir)
except FileNotFoundError:
    show_help('You need to run the download-step first.')
print('-- changed to: {}'.format(os.getcwd()))

print('-- reading input data')
in_files = b_iotools.findfiles('preproc', '.*\\.txt', file_limit=file_limit)
tokens = []
for in_file in in_files:
    file_tokens = b_iotools.read_file_to_list(in_file, ignore_empty_lines=True)
    tokens.append(file_tokens)

print('-- generating term dictionary')
dictionary = corpora.Dictionary(tokens)

print('-- converting tokenized documents into bag of words')
corpus = [dictionary.doc2bow(text) for text in tokens]

print('-- generating lda model')
ldamodel = gensim.models.ldamulticore.LdaMulticore(
    corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes,
    workers=4)

for topic in ldamodel.print_topics(num_topics=lda_topics, num_words=6):
    print(topic)


def main():
    pass
