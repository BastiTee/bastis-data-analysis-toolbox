#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtain topics from given text content."""

from gensim import corpora
import gensim.models.word2vec
from bptbx import b_iotools, b_cmdprs
from robota import r_util

r_util.notify_start(__file__)

# ------------------------------------------------------------ CMD-LINE-PARSING
prs = b_cmdprs.TemplateArgumentParser(
    description='' +
    'Generate LDA-based topic models')
prs.add_dir_in()
prs.add_dir_out(ch_dir=True)
prs.add_verbose()
args = prs.parse_args()
# -----------------------------------------------------------------------------

lda_topics = 5
lda_passes = 2
r_util.log('reading input data')
in_files = r_util.read_valid_inputfiles(args.i)
tokens = []
for in_file in in_files:
    file_tokens = b_iotools.read_file_to_list(in_file, ignore_empty_lines=True)
    tokens.append(file_tokens)

r_util.log('generating term dictionary')
dictionary = corpora.Dictionary(tokens)

r_util.log('converting tokenized documents into bag of words')
corpus = [dictionary.doc2bow(text) for text in tokens]

r_util.log('generating lda model')
ldamodel = gensim.models.ldamulticore.LdaMulticore(
    corpus, num_topics=lda_topics, id2word=dictionary, passes=lda_passes,
    workers=4)

for topic in ldamodel.print_topics(num_topics=lda_topics, num_words=6):
    r_util.log(topic)


def main():
    """Void main entry."""
    pass
