#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
#trump-sample-article.bdatbx
# http://bdewilde.github.io/blog/2014/09/23/intro-to-automatic-keyphrase-extraction/
#
# https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
# NN | Noun, singular or mass |
# NNS | Noun, plural |
# NNP | Proper noun, singular |
# NNPS | Proper noun, plural |
# JJ | Adjective |
# JJR | Adjective, comparative |
# JJS | Adjective, superlative |


def get_stemmer_for_language(language):
    return nltk.stem.snowball.SnowballStemmer(language, ignore_stopwords=False)

def get_stopwords_for_language(language):
    from bdatbx import b_util
    from bptbx import b_iotools
    import nltk
    stop_words = nltk.corpus.stopwords.words(language)
    path = b_util.load_resource_file('stopwords_{}_add.txt'.format(language))
    new_stopwords = b_iotools.read_file_to_list(path)
    b_util.log('Will add {} stopwords from {} to {} stopword list'.format(
        len(new_stopwords), path, language))
    stop_words = set(stop_words + new_stopwords)
    return stop_words


def score_terms_by_textrank(text, language='german'):
    import nltk, itertools, networkx, nltk, string, re

    stop_words = get_stopwords_for_language(language)
    stemmer = get_stemmer_for_language(language)
    stop_words = set([stemmer.stem(stop_word) for stop_word in stop_words])
    allowed_pos_tags=set(['FW', 'JJ','JJR','JJS','NN','NNP','NNS','NNPS'])
    token_2_word_dict = {}
    all_tokens = []
    all_token_sentences = []

    for sentence in nltk.sent_tokenize(text):
        all_sentence_words = []
        for token in nltk.tokenize.WordPunctTokenizer().tokenize(sentence):
            regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
            if not re.match(regex, token):
                continue
            original_token = token
            token = stemmer.stem(token)
            try:
                token_2_word_dict[token]
            except KeyError:
                token_2_word_dict[token] = {}
            try:
                token_2_word_dict[token][original_token] += 1
            except KeyError:
                token_2_word_dict[token][original_token] = 1
            all_sentence_words.append(token)
            all_tokens.append(token)
        all_token_sentences.append(all_sentence_words)

    tagged_tokens = itertools.chain.from_iterable(   nltk.pos_tag_sents(all_token_sentences))

    candidate_tokens = [word for word, tag in tagged_tokens
                  if tag in allowed_pos_tags and word not in stop_words]

    # build graph, each node is a unique candidate
    graph = networkx.Graph()
    graph.add_nodes_from(set(candidate_tokens))
    # iterate over word-pairs, add unweighted edges into graph
    def pairwise(iterable):
        """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)
    for w1, w2 in pairwise(candidate_tokens):
        if w2:
            graph.add_edge(*sorted([w1, w2]))
    # score nodes using default pagerank algorithm, sort by score, keep top n_keywords
    n_keywords = 0.05
    ranks = networkx.pagerank(graph)
    if 0 < n_keywords < 1:
        n_keywords = int(round(len(candidate_tokens) * n_keywords))
    word_ranks = {word_rank[0]: word_rank[1]
                  for word_rank in sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:n_keywords]}
    keywords = set(word_ranks.keys())
    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(all_tokens):
        if i < j:
            continue
        if word in keywords:
            kp_words = list(itertools.takewhile(lambda x: x in keywords, all_tokens[i:i+10]))
            avg_pagerank = sum(word_ranks[w] for w in kp_words) / float(len(kp_words))
            keyphrases[' '.join(kp_words)] = avg_pagerank
            j = i + len(kp_words)


    # replace phrases with most common orgiginal
    # keyphrases_original = {}
    # for keyphrase in keyphrases:
    #     import operator
    #     new_keyphrase = []
    #     for subphrase in keyphrase.split(' '):
    #         org_dict = token_2_word_dict[subphrase]
    #         org_dict = sorted(
    #             org_dict.items(), key=operator.itemgetter(1), reverse=True)
    #         org_subphrase = org_dict[0][0]
    #         new_keyphrase.append(org_subphrase)
    #     new_keyphrase = ' '.join(new_keyphrase)
    #     keyphrases_original[new_keyphrase] = keyphrases[keyphrase]
    keyphrases_original = keyphrases

    return sorted(keyphrases_original.items(), key=lambda x: x[1], reverse=True)

if __name__ == '__main__':
    import nltk
    from bptbx.b_iotools import read_file_to_list
    from os import path

    nltk.data.path.append('nltk-data')

    text = ' '.join(read_file_to_list(path.join(
    'bdatbx_test/resource/trump-sample-article.bdatbx')))

    terms = score_terms_by_textrank(text)
    i = 0
    for term, rank in terms:
        print('{}\t{}'.format(rank, term))
        i += 1
        if i == 15:
            break
