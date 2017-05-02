#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utility module to extract the publish date of a webpage.

This module is based on https://github.com/Webhose/article-date-extractor
licensed under MIT and has been extended to support Python 3, a more
sophisticated date-parser and more corner cases.

The MIT License (MIT)

Copyright (c) 2015 Webhose.io

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re
import json
from dateparser import parse
from bs4 import BeautifulSoup
from robota import r_util

PATTERNS = ['timestamp', 'publish', 'date', 'created', 'time']


def _parse_str_date(ds, min_epoch, max_epoch):
    try:
        # catch some bad data corner cases
        if ds is None:  # empty strings
            return None
        if len(ds) < 4 or len(ds) > 50:  # too long/short strings
            return None
        if re.search('[0-9]+', ds) is None:  # no numbers in string
            return None
        if re.match('^-?[0-9]+$', ds):  # limit number-only dates
            try:
                dsi = int(ds)
                if dsi < 0:
                    return None
            except Exception:
                return None
        # clean up candidate string
        ds = re.sub('^[^a-zA-Z0-9]', '', ds)
        ds = re.sub('[^a-zA-Z0-9]$', '', ds)

        dto = parse(ds)
        epoch = int(dto.strftime('%s'))

        if epoch < min_epoch or epoch > max_epoch:
            return None

        # print('{} >> {} < {} | {}'.format(ds, dto, epoch, valid))
        return dto
    except Exception as e:
        return None


def _extract_from_url(url, min_epoch, max_epoch):

    matcher = re.search(
        r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9]' +
        '[\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if matcher:
        return _parse_str_date(matcher.group(0), min_epoch, max_epoch), 'url'
    return None, None


def _extract_from_ldjson(parsed_html, min_epoch, max_epoch):
    try:
        script = parsed_html.find('script', type='application/ld+json')
        if script is None:
            return None, None
        data = json.loads(script.text)
        if data.keys() is None or len(data.keys()) < 1:
            return None, None
        json_keys = [json_key for json_key in data.keys()
                     for pattern in PATTERNS if pattern in json_key]
        for json_key in json_keys:
            try:
                json_date = _parse_str_date(
                    data[json_key], min_epoch, max_epoch)
                if json_date:
                    return json_date, 'json-ld-{}'.format(json_key)
            except Exception as e:
                pass
    except Exception as e:
        return None, None
    return None, None


def _extract_from_meta(parsed_html, min_epoch, max_epoch):

    for meta_element in parsed_html.findAll('meta'):
        meta_content = meta_element.get('content', '').strip()
        if not meta_content or len(meta_content) < 4 or len(meta_content) > 50:
            continue
        meta_cand = ' '.join(set([meta_element.get(hint) for hint in [
            'name', 'property', 'itemprop', 'http-equiv']
            if meta_element.get(hint, None)]))
        for pattern in PATTERNS:
            if pattern in meta_cand:
                dt = _parse_str_date(meta_content, min_epoch, max_epoch)
                if dt:
                    return dt, 'meta-{}'.format(meta_cand)
    return None, None


def _extract_from_html_tag(parsed_html, min_epoch, max_epoch):

    for time in parsed_html.findAll('time'):
        datetime = time.get('datetime', '')
        if len(datetime) > 0:
            date_parsed = _parse_str_date(datetime, min_epoch, max_epoch)
            if date_parsed:
                return date_parsed, 'html-time-datetime'
        date_parsed = _parse_str_date(time.text, min_epoch, max_epoch)
        if date_parsed:
            return date_parsed, 'html-time-text'

    elements = ['abbr', 'span', 'p', 'div', 'h1', 'h2', 'h3', 'li']
    for tag in parsed_html.find_all(elements):
        indicator = None
        indicator_src = None
        try:
            classes = set(tag['class'])
            indicator = ' '.join(classes)
            indicator_src = 'class'
        except Exception as e:
            pass
        if not indicator:
            try:
                classes = set(tag['itemprop'])
                indicator = ' '.join(classes)
                indicator_src = 'itemprop'
            except Exception as e:
                pass
        if not indicator:
            continue
        useful_indicator = False
        for pattern in PATTERNS:
            if pattern in indicator:
                useful_indicator = True
                break
        if useful_indicator is False:
            continue
        date_text = tag.string
        parsed_date = _parse_str_date(date_text, min_epoch, max_epoch)
        if parsed_date is not None:
            return parsed_date, 'html-{}-{}-{}'.format(
                tag.name, indicator_src, '-'.join(classes))
        date_text = tag.text
        parsed_date = _parse_str_date(date_text, min_epoch, max_epoch)
        if parsed_date is not None:
            return parsed_date, 'html-{}-{}-{}'.format(
                tag.name, indicator_src, '-'.join(classes))

    return None, None


def _extract_using_newspaper(html, uri, min_epoch, max_epoch):
    from newspaper import Article
    article = Article(uri)
    article.download(html=html)
    article.parse()
    date_text = '{}'.format(article.publish_date)
    parsed_date = _parse_str_date(date_text, min_epoch, max_epoch)
    if parsed_date is not None:
        return parsed_date, 'newspaper'
    return None, None


def extract_article_pubdate(uri, html, min_epoch=0, max_epoch=4102444800):
    """Try to extract the publish date from given URL/HTML content.

    By default allowed dates can range between 01.01.1970 and 01.01.2100.
    """
    try:
        if len(html) == 0:
            raise ValueError('Input HTML is empty')

        parsed_html = BeautifulSoup(html, 'html.parser')

        res_date, res_hint = _extract_from_ldjson(
            parsed_html, min_epoch, max_epoch)
        if res_date:
            return res_date, res_hint

        res_date, res_hint = _extract_from_meta(
            parsed_html, min_epoch, max_epoch)
        if res_date:
            return res_date, res_hint

        res_date, res_hint = _extract_from_html_tag(
            parsed_html, min_epoch, max_epoch)
        if res_date:
            return res_date, res_hint

        # ---------------------------------------------------------------
        # res_date, res_hint = _extract_using_newspaper(
        #     html, uri, min_epoch, max_epoch)
        # if res_date:
        #     return res_date, res_hint
        # --- DEACTIVATED FOR NOW SINCE IT DOESN'T IMPROVE DETECTION RATE

        res_date, res_hint = _extract_from_url(uri, min_epoch, max_epoch)
        if res_date:
            return res_date, res_hint

    except Exception as e:
        r_util.logerr('{} - {}'.format(e, uri))

    return None, None


def get_current_epoch():
    """Return the current epoch."""
    import calendar
    import time
    return calendar.timegm(time.gmtime())


if __name__ == '__main__':
    from requests import get
    from sys import argv, exit
    from bptbx import b_iotools
    try:
        url = argv[1]
    except IndexError:
        print('No URL provided')
        exit(1)
    html = None
    if not url.startswith('http'):
        html = '\n'.join(b_iotools.read_file_to_list(url))
    else:
        html = get(url, timeout=10).text
    if not html:
        print('Input location invalid')
        exit(1)
    date, hint = extract_article_pubdate(url, html)
    if not hint:
        hint = '??'
    if not date:
        date = '??'
    print('{} | {} | {}'.format(hint.ljust(8), str(date).ljust(25), url[:80]))
