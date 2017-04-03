#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Based on http://bdewilde.github.io/blog/2014/09/23/
# intro-to-automatic-keyphrase-extraction/

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

def get_stemmed_stopwords_for_language(language):
    stop_words = get_stopwords_for_language(language)
    stemmer = get_stemmer_for_language(language)
    return set([stemmer.stem(stop_word) for stop_word in stop_words])

def score_terms_by_textrank(text, language='german'):
    import nltk, itertools, networkx, nltk, string, re

    stop_words = get_stemmed_stopwords_for_language(language)
    stemmer = get_stemmer_for_language(language)

    allowed_pos_tags=set(['FW', 'JJ','JJR','JJS','NN','NNP','NNS','NNPS'])
    token_2_word_dict = {}
    all_tokens = []
    all_token_sentences = []
    ngram_buffer = ["", "", ""]
    ngram_buffer_org = ["", "", ""]
    max_ngram_len = 3
    window_shift = 2

    for sentence in nltk.sent_tokenize(text):
        all_sentence_words = []
        for token in nltk.tokenize.WordPunctTokenizer().tokenize(sentence):
            regex = '[a-zA-ZäöüÄÖÜß0-9]+'  # at least one of those must appear
            if not re.match(regex, token):
                continue
            original_token = token
            token = stemmer.stem(token)
            for idx in reversed(range(0, max_ngram_len-1)):
                ngram_buffer[idx+1] = ngram_buffer[idx]
                ngram_buffer_org[idx+1] = ngram_buffer_org[idx]
            ngram_buffer[0] = token
            ngram_buffer_org[0] = original_token

            for idx in range(0, max_ngram_len-window_shift):
                if window_shift > 0:
                    window_shift -= 1
                ngram = ' '.join(reversed(ngram_buffer[0:idx+1])).strip()
                ngram_org = ' '.join(reversed(ngram_buffer_org[0:idx+1])).strip()
                try:
                    token_2_word_dict[ngram]
                except KeyError:
                    token_2_word_dict[ngram] = {}
                try:
                    token_2_word_dict[ngram][ngram_org] += 1
                except KeyError:
                    token_2_word_dict[ngram][ngram_org] = 1
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


    keyphrases_original = {}
    for keyphrase in keyphrases:
        import operator
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

    return sorted(keyphrases_original.items(), key=lambda x: x[1], reverse=True)

if __name__ == '__main__':
    import nltk
    from bdatbx import b_parse
    from bptbx.b_iotools import read_file_to_list
    from os import path
    from requests import get
    from sys import argv, exit

    nltk.data.path.append('nltk-data')

    url = argv[1]
    if not url:
        print('No URL given.')
        exit(1)

    in_html = None
    try:
        r = get(url, timeout=10)
        in_html = r.text
    except Exception as e:
        print('Could not download \'{}\' with error: {}'.format(url, e))
        exit(1)

    in_text = b_parse.extract_main_text_content(in_html)

    terms = score_terms_by_textrank(in_text)
    i = 0
    for term, rank in terms:
        print('{}\t{}'.format(rank, term))
        i += 1
        if i == 15:
            break
