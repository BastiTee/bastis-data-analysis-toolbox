"""Parse, match or convert recurring data formats."""


def parse_basic_money_format_to_float(amount):
    """Convert money format, e.g., '-1.000,00' or '123.32' to a float."""
    if amount is None:
        raise ValueError('Amount cannot be None')
    from re import match, sub
    valid_format = match('-?[0-9\.]+,[0-9]{2}', amount)
    if valid_format is None:
        raise ValueError(
            'Money amount does not match format \'-?[0-9\.]+,[0-9]{2}\'')
    amount = sub('\.', '', amount)
    amount = sub(',', '.', amount)
    amount = float(amount)
    return amount


def contains(pattern, string):
    """Quickly test if a string contains a pattern."""
    if pattern is None:
        raise ValueError('Pattern cannot be None')
    if string is None:
        return False
    from re import match, IGNORECASE
    if match('.*{}.*'.format(pattern), string, IGNORECASE):
        return True
    return False


def get_domain_from_uri(uri):
    """Extract the domain from the given URI string."""
    if not uri:
        return None
    from urllib import parse
    from re import sub
    netloc = parse.urlparse(uri).netloc
    netloc = sub(':[^:]+$', '', netloc)  # get rid of port numbers
    return netloc


def extract_main_text_content(html):
    """A method to extract the main content of a given HTML page.

    This code has been adapted from http://nirmalpatel.com/fcgi/hn.py (GPLv3)
    written by Nirmal Patel.
    """
    import re
    from bs4 import BeautifulSoup

    negative = re.compile('comment|meta|footer|footnote|foot')
    positive = re.compile('post|hentry|entry|content|text|body|article')
    # punctation = re.compile('''[!'#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]''')

    replace_brs = re.compile('<br */? *>[ \r\n]*<br */? *>')
    html = re.sub(replace_brs, '</p><p>', html)

    try:
        soup = BeautifulSoup(html, 'html.parser')
    except:
        return ''

    # REMOVE SCRIPTS
    for s in soup.findAll('script'):
        s.extract()

    all_paragraphs = soup.findAll('p')
    top_parent = None

    parents = []
    for paragraph in all_paragraphs:

        parent = paragraph.parent

        if (parent not in parents):
            parents.append(parent)
            parent.score = 0

            if (parent.has_attr('class')):
                if (negative.match(str(parent['class']))):
                    parent.score -= 50
                if (positive.match(str(parent['class']))):
                    parent.score += 25

            if (parent.has_attr('id')):
                if (negative.match(str(parent['id']))):
                    parent.score -= 50
                if (positive.match(str(parent['id']))):
                    parent.score += 25

        if (parent.score is None):
            parent.score = 0

        # ''.join(paragraph.findAll(text=True))
        inner_text = paragraph.renderContents()
        if (len(inner_text) > 10):
            parent.score += 1

        parent.score += str(inner_text).count(',')

    for parent in parents:
        if ((not top_parent) or (parent.score > top_parent.score)):
            top_parent = parent

    if (not top_parent):
        return ''

    # REMOVE LINK'D STYLES
    style_links = soup.findAll('link', attrs={'type': 'text/css'})
    for s in style_links:
        s.extract()

    # REMOVE ON PAGE STYLES
    for s in soup.findAll('style'):
        s.extract()

    # CLEAN STYLES FROM ELEMENTS IN TOP PARENT
    for ele in top_parent.findAll(True):
        del(ele['style'])
        del(ele['class'])

    _extract_main_text_content_remove_divs(top_parent)
    _extract_main_text_content_clean(top_parent, 'form')
    _extract_main_text_content_clean(top_parent, 'object')
    _extract_main_text_content_clean(top_parent, 'iframe')

    full_text = top_parent.renderContents().decode('utf-8')
    full_text_final = []
    for line in full_text.split('\n'):
        if not line.strip():
            continue
        line = re.sub('<[^>]+>', '', line).strip()
        if line:
            full_text_final.append(line)
    return '\n'.join(full_text_final)


def _extract_main_text_content_clean(top, tag, min_words=10000):
    tags = top.findAll(tag)
    for t in tags:
        if (str(t.renderContents()).count(' ') < min_words):
            t.extract()


def _extract_main_text_content_remove_divs(parent):
    divs = parent.findAll('div')
    for d in divs:
        p = len(d.findAll('p'))
        img = len(d.findAll('img'))
        li = len(d.findAll('li'))
        a = len(d.findAll('a'))
        embed = len(d.findAll('embed'))
        pre = len(d.findAll('pre'))
        code = len(d.findAll('code'))

        if (str(d.renderContents()).count(',') < 10):
            if ((pre == 0) and (code == 0)):
                if (
                        (img > p) or (li > p) or (a > p) or (p == 0)
                        or (embed > 0)):
                    d.extract()
