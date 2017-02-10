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

lda_topics = 5
lda_passes = 2
print('-- reading input data')
in_files = b_iotools.findfiles(input_dir, '.*\\.txt')
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
