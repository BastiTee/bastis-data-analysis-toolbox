r"""Functions for preprocessing text data."""


def get_stemmer_for_language(language):
    import nltk
    return nltk.stem.snowball.SnowballStemmer(language, ignore_stopwords=False)


def get_allowed_postags(language):
    # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    # https://www.linguistik.hu-berlin.de/de/institut/professuren/korpuslinguistik/mitarbeiter-innen/hagen/STTS_Tagset_Tiger
    apt = {
        'english': set(
            ['FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS']),
        'german': set(
            ['FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS']),
        'german_stanford': set(
            ['FM', 'ADJA', 'ADJD', 'NN', 'NE']),
    }
    return apt[language]


def get_stopwords_for_language(language):
    from bdatbx import b_util
    from bptbx import b_iotools
    import nltk
    stop_words = nltk.corpus.stopwords.words(language)
    path = b_util.get_resource_filepath(
        'stopwords_{}_add.txt'.format(language))
    new_stopwords = b_iotools.read_file_to_list(path)
    b_util.log('Will add {} stopwords from {} to {} stopword list'.format(
        len(new_stopwords), path, language))
    stop_words = set(stop_words + new_stopwords)
    return stop_words


def get_stemmed_stopwords_for_language(language):
    stop_words = get_stopwords_for_language(language)
    stemmer = get_stemmer_for_language(language)
    return set([stemmer.stem(stop_word) for stop_word in stop_words])


def get_token_sentences(text):
    import nltk
    token_sentences = []
    for s in nltk.sent_tokenize(text):
        sentence = []
        for t in nltk.tokenize.WordPunctTokenizer().tokenize(s):
            sentence.append(t)
        token_sentences.append(sentence)
    return token_sentences


def print_postag_table(tagged_tokens, print=False):
    from bdatbx import b_util
    if not print:
        return
    t = []
    for key, val in list(tagged_tokens)[:100]:
        t.append([key, val])
    b_util.print_table(t, headers=['Token', 'POS-TAG'])


def postag_sentences(tok_sen, language, sanity_print=False):
    import itertools
    import nltk
    tagged_tokens = itertools.chain.from_iterable(
        nltk.pos_tag_sents(tok_sen))
    print_postag_table(tagged_tokens, sanity_print)
    return tagged_tokens


def postag_sentences_stanford(tok_sen, language, sanity_print=False):
    import itertools
    import nltk
    import os
    from bdatbx import b_util
    pos_tagger_path = b_util.get_resource_filepath('stanford-postagger')
    pos_tagger = nltk.tag.stanford.StanfordPOSTagger(
        os.path.join(pos_tagger_path, 'models', 'german-fast.tagger'), path_to_jar=os.path.join(pos_tagger_path, 'stanford-postagger.jar'),
        encoding='utf-8')
    output = pos_tagger.tag_sents(tok_sen)
    tagged_tokens = itertools.chain.from_iterable(output)
    print_postag_table(tagged_tokens, sanity_print)
    return tagged_tokens
