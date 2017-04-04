#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs, b_util
b_util.notify_start(__file__)
prs = b_cmdprs.init('Generate LDA-based topic models')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
# -----------------------------------------------------------------------------

import os
from argparse import ArgumentParser
from gensim import corpora, models
import gensim.models.word2vec
from bptbx import b_iotools

lda_topics = 5
lda_passes = 2
b_util.log('reading input data')
in_files = b_util.read_valid_inputfiles(args.i)
tokens = []
for in_file in in_files:
    file_tokens = b_iotools.read_file_to_list(in_file, ignore_empty_lines=True)
    tokens.append(file_tokens)

b_util.log('generating term dictionary')
dictionary = corpora.Dictionary(tokens)

b_util.log('converting tokenized documents into bag of words')
corpus = [dictionary.doc2bow(text) for text in tokens]

b_util.log('generating lda model')
ldamodel = gensim.models.ldamulticore.LdaMulticore(
    corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes,
    workers=4)

for topic in ldamodel.print_topics(num_topics=lda_topics, num_words=6):
    b_util.log(topic)


def main():
    pass
