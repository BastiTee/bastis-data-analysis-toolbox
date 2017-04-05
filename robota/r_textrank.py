#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Implementation of textrank algorithm for keyword extration.

Based on http://bdewilde.github.io/blog/2014/09/23/
intro-to-automatic-keyphrase-extraction/
"""


def score_terms_by_textrank(text, language='german'):
    """Return scored textrank terms for given text and language."""
    import itertools
    import networkx
    import re
    import operator
    from robota import r_preproc, r_util

    stop_words = r_preproc.get_stemmed_stopwords_for_language(language)
    stemmer = r_preproc.get_stemmer_for_language(language)
    tok_sen = r_preproc.get_token_sentences(text)
    allowed_pos_tags = r_preproc.get_allowed_postags(language + "_stanford")
    tok_sen_postag = r_preproc.postag_sentences_stanford(
        tok_sen, language)

    all_tokens = []
    candidate_tokens = []

    token_2_word_dict = {}
    ngram_buffer = ["", "", ""]
    ngram_buffer_org = ["", "", ""]
    max_ngram_len = 3
    window_shift = 2

    for token, pos_tag in list(tok_sen_postag):
        regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
        if not re.match(regex, token):
            continue
        original_token = token
        token = stemmer.stem(token)
        all_tokens.append(token)
        if token in stop_words:
            continue
        if pos_tag not in allowed_pos_tags:
            continue
        candidate_tokens.append(token)

        for idx in reversed(range(0, max_ngram_len - 1)):
            ngram_buffer[idx + 1] = ngram_buffer[idx]
            ngram_buffer_org[idx + 1] = ngram_buffer_org[idx]
        ngram_buffer[0] = token
        ngram_buffer_org[0] = original_token

        for idx in range(0, max_ngram_len - window_shift):
            if window_shift > 0:
                window_shift -= 1
            ngram = ' '.join(reversed(ngram_buffer[0:idx + 1])).strip()
            ngram_org = ' '.join(
                reversed(ngram_buffer_org[0:idx + 1])).strip()
            try:
                token_2_word_dict[ngram]
            except KeyError:
                token_2_word_dict[ngram] = {}
            try:
                token_2_word_dict[ngram][ngram_org] += 1
            except KeyError:
                token_2_word_dict[ngram][ngram_org] = 1

    r_util.log('all-tokens:  {}'.format(len(all_tokens)))
    r_util.log('cand-tokens: {}'.format(len(candidate_tokens)))

    # build graph, each node is a unique candidate
    graph = networkx.Graph()
    graph.add_nodes_from(set(candidate_tokens))
    # iterate over word-pairs, add unweighted edges into graph

    for w1, w2 in _pairwise(candidate_tokens):
        if w2:
            graph.add_edge(*sorted([w1, w2]))

    # score nodes using default pagerank algorithm, sort by score, keep top
    # n_keywords
    n_keywords = 0.05
    ranks = networkx.pagerank(graph)
    if 0 < n_keywords < 1:
        n_keywords = int(round(len(candidate_tokens) * n_keywords))
    word_ranks = {
        word_rank[0]: word_rank[1]
        for word_rank in sorted(ranks.items(), key=lambda x: x[1],
                                reverse=True)[:n_keywords]}
    keywords = set(word_ranks.keys())

    # merge keywords into keyphrases
    keyphrases = {}
    j = 0
    for i, word in enumerate(all_tokens):
        if i < j:
            continue
        if word in keywords:
            kp_words = list(itertools.takewhile(
                lambda x: x in keywords, all_tokens[i:i + 10]))
            avg_pagerank = sum(word_ranks[w]
                               for w in kp_words) / float(len(kp_words))
            keyphrases[' '.join(kp_words)] = avg_pagerank
            j = i + len(kp_words)

    keyphrases_original = {}
    for keyphrase in keyphrases:
        new_keyphrase = []

        try:
            org_dict = token_2_word_dict[keyphrase]
            org_dict = sorted(
                org_dict.items(), key=operator.itemgetter(1), reverse=True)
            new_keyphrase = org_dict[0][0]
        except KeyError:
            for subphrase in keyphrase.split(' '):
                org_dict = token_2_word_dict[subphrase]
                org_dict = sorted(
                    org_dict.items(), key=operator.itemgetter(1), reverse=True)
                org_subphrase = org_dict[0][0]
                new_keyphrase.append(org_subphrase)
            new_keyphrase = ' '.join(new_keyphrase)
        keyphrases_original[new_keyphrase] = keyphrases[keyphrase]

    return sorted(
        keyphrases_original.items(), key=lambda x: x[1], reverse=True)


def _pairwise(iterable):
    """Uses: s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    import itertools
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


if __name__ == '__main__':
    import nltk
    from robota import r_parse
    from requests import get
    from sys import argv, exit

    nltk.data.path.append('nltk-data')

    try:
        url = argv[1]
    except IndexError:
        print('No URL given.')
        exit(1)

    in_html = None
    try:
        r = get(url, timeout=10)
        in_html = r.text
    except Exception as e:
        print('Could not download \'{}\' with error: {}'.format(url, e))
        exit(1)

    in_text = r_parse.extract_main_text_content(in_html)

    terms = score_terms_by_textrank(in_text)
    # i = 0
    for term, rank in terms:
        print('{}\t{}'.format(rank, term))
        # i += 1
        # if i == 15:
        #     break
