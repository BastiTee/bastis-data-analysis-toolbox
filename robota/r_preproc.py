"""Functions for preprocessing text data."""


def install_nltk_environment():
    """Run a default NLTK installation procedure.

    This will create a 'nltk-data' folder on your disk in the current
    working directory."""
    from nltk import downloader, data as nltk_data
    from os import path
    for module in ['averaged_perceptron_tagger', 'stopwords', 'punkt']:
        downloader.download(module, download_dir='nltk-data', quiet=True)
    nltk_data.path.append(path.abspath('nltk-data'))


def preprocess_string_to_tokens(text, language='english'):
    """Run a chain of typical preprocessing steps on the given text."""
    try:
        tokens = get_token_sentences(text)
        tokens = [subsubtokens for subtokens in tokens
                  for subsubtokens in subtokens]
        tokens = sanitize_tokens(tokens)
        tokens = remove_nonwords(tokens, 2)
        sw = get_stopwords_for_language(language, True)
        tokens = stopword_removal(tokens, sw)
        stemmer = get_stemmer_for_language(language)
        tokens = stem(tokens, stemmer)[0]
        return tokens
    except LookupError:
        install_nltk_environment()
        return preprocess_string_to_tokens(text)


def get_stemmer_for_language(language):
    """Return stemmer for given language."""
    import nltk
    return nltk.stem.snowball.SnowballStemmer(language, ignore_stopwords=False)


def get_allowed_postags(language):
    """Return a list of allowed POS-tags depending on language.

    There are two versions popular.
    1) PENN Treebank
    https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    2) STSS Tiger Tagset
    https://www.linguistik.hu-berlin.de/de/institut/professuren/korpuslinguistik/mitarbeiter-innen/hagen/STTS_Tagset_Tiger
    """
    apt = {
        'english': set(
            ['FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS']),
        'german': set(
            ['FW', 'JJ', 'JJR', 'JJS', 'NN', 'NNP', 'NNS', 'NNPS']),
        'german_stanford': set(
            ['FM', 'ADJA', 'ADJD', 'NN', 'NE']),
    }
    return apt[language]


def stem(tokens, stemmer, skip_pattern=None, skip_process=lambda x: x):
    from re import match, IGNORECASE
    stem_2_source_dict = {}
    stemmed_tokens = []
    for token in tokens:
        if not skip_pattern or not match(skip_pattern, token, IGNORECASE):
            stem = stemmer.stem(token)
            stemmed_tokens.append(stem)
        else:
            stem = skip_process(token)
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
    return stemmed_tokens, stem_2_source_dict


def sanitize_tokens(tokens, protected_chars=''):
    from re import sub
    clean_tokens = []
    for token in tokens:
        if not token:
            continue
        token = token.strip()
        bad_chars = '[^a-zA-Z0-9äöüÄÖÜß\-&' + protected_chars + ']'
        clean_token = sub(bad_chars, '', token)
        if not clean_token or len(clean_token) == 0:
            continue
        # print('{} >> {}'.format(token, clean_token))
        if clean_token:
            clean_tokens.append(clean_token)
    return clean_tokens


def get_stopwords_for_language(language, quiet=False):
    """Return a set of stopwords for the given language."""
    from robota import r_util
    from bptbx import b_iotools
    import nltk
    stop_words = nltk.corpus.stopwords.words(language)
    path = r_util.get_resource_filepath(
        'stopwords_{}_add.txt'.format(language))
    new_stopwords = b_iotools.read_file_to_list(path)
    if not quiet:
        r_util.log('Will add {} stopwords from {} to {} stopword list'.format(
            len(new_stopwords), path, language))
    stop_words = set(stop_words + new_stopwords)
    return stop_words


def get_stemmed_stopwords_for_language(language):
    """Return a set of stemmed stopwords for the given language."""
    stop_words = get_stopwords_for_language(language)
    stemmer = get_stemmer_for_language(language)
    return set([stemmer.stem(stop_word) for stop_word in stop_words])


def get_token_sentences(text):
    """Split up given text into sentences and tokens."""
    import nltk
    token_sentences = []
    for s in nltk.sent_tokenize(text):
        sentence = []
        for t in nltk.tokenize.WordPunctTokenizer().tokenize(s):
            sentence.append(t)
        token_sentences.append(sentence)
    return token_sentences


def remove_nonwords(tokens, min_len=0, remove_numbers=False):
    from re import match
    from robota import r_math
    regex = '.*[a-zA-ZäöüÄÖÜß0-9]+.*'  # at least one of those must appear
    filtered_tokens = [
        token for token in tokens
        if match(regex, token) and len(token) >= min_len
    ]
    if remove_numbers:
        filtered_tokens = [
            token for token in filtered_tokens
            if not r_math.is_number(token)
        ]
    return filtered_tokens


def stopword_removal(tokens, stopwords):
    filtered_tokens = []
    for token in tokens:
        if token not in stopwords:
            filtered_tokens.append(token)
    return filtered_tokens


def postag_sentences(tok_sen, language, sanity_print=False):
    """Create POS-tags for given sentence/token list of lists."""
    import itertools
    import nltk
    tagged_tokens = itertools.chain.from_iterable(
        nltk.pos_tag_sents(tok_sen))
    _print_postag_table(tagged_tokens, sanity_print)
    return tagged_tokens


def postag_sentences_stanford(tok_sen, language, sanity_print=False):
    """Create POS-tags for given sentence/token list of lists."""
    import itertools
    import nltk
    import os
    from robota import r_util
    pos_tagger_path = r_util.get_resource_filepath('stanford-postagger')
    pos_tagger = nltk.tag.stanford.StanfordPOSTagger(
        os.path.join(pos_tagger_path, 'models', 'german-fast.tagger'),
        path_to_jar=os.path.join(
            pos_tagger_path, 'stanford-postagger.jar'),
        encoding='utf-8')
    output = pos_tagger.tag_sents(tok_sen)
    tagged_tokens = itertools.chain.from_iterable(output)
    _print_postag_table(tagged_tokens, sanity_print)
    return tagged_tokens


def _print_postag_table(tagged_tokens, print=False):
    from robota import r_util
    if not print:
        return
    t = []
    for key, val in list(tagged_tokens)[:100]:
        t.append([key, val])
    r_util.print_table(t, headers=['Token', 'POS-TAG'])
