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

PATTERNS = ['publish', 'date', 'created', 'time']


def _parse_str_date(ds, mine, maxe):
    try:
        # catch some bad data corner cases
        if ds is None:  # empty strings
            return None
        if ds is None or len(ds) < 4 or len(ds) > 50:  # too long/short strings
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

        if epoch < mine or epoch > maxe:
            return None

        # print('{} >> {} < {} | {}'.format(ds, dto, epoch, valid))
        return dto
    except Exception as e:
        # print('ERR >> {}'.format(e))
        return None


def _extract_from_url(url, mine, maxe):

    matcher = re.search(
        r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9]' +
        '[\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if matcher:
        return _parse_str_date(matcher.group(0), mine, maxe)
    return None


def _extract_from_ldjson(parsed_html, mine, maxe):
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
                json_date = _parse_str_date(data[json_key], mine, maxe)
                if json_date:
                    return json_date, 'json-ld'
            except Exception as e:
                pass
    except Exception as e:
        return None, None
    return None, None


def _extract_from_meta(parsed_html, mine, maxe):

    for meta_element in parsed_html.findAll('meta'):
        meta_content = meta_element.get('content', '').strip()
        if not meta_content or len(meta_content) < 4 or len(meta_content) > 50:
            continue
        meta_cand = ' '.join([meta_element.get(hint) for hint in [
            'name', 'property', 'itemprop', 'http-equiv']
            if meta_element.get(hint, None)])
        for pattern in PATTERNS:
            if pattern in meta_cand:
                dt = _parse_str_date(meta_content, mine, maxe)
                if dt:
                    return dt, 'meta'
    return None, None


def _extract_from_html_tag(parsed_html, mine, maxe):
    # <time>
    for time in parsed_html.findAll('time'):
        datetime = time.get('datetime', '')
        if len(datetime) > 0:
            de = _parse_str_date(datetime, mine, maxe)
            if de:
                return de

        datetime = time.get('class', '')
        if len(datetime) > 0 and datetime[0].lower() == 'timestamp':
            de = _parse_str_date(time.string, mine, maxe)
            if de:
                return de

        datetext = _parse_str_date(time.text, mine, maxe)
        if datetext:
            return datetext

    tag = parsed_html.find('span', {'itemprop': 'datePublished'})
    if tag is not None:
        date_text = tag.get('content')
        if date_text is None:
            date_text = tag.text
        if date_text is not None:
            return _parse_str_date(date_text, mine, maxe)

    # class=
    # re.compile(
    # 'pubdate|timestamp|post-date|date-header|' +
    #     'article_date|articledate|date'
    elements = ['abbr', 'span', 'p', 'div', 'h1', 'h2', 'h3', 'li']
    # classes = [
    #     'blogheader', 'pubdate', 'published', 'timestamp', 'post-date',
    #     'date-header', 'article_date', 'articledate', 'date',
    #     'content-column', 'one_half', 'theTime']
    # for class_ in classes:
    for tag in parsed_html.find_all(elements):
        class_ = None
        try:
            class_ = ' '.join(tag['class'])
        except Exception as e:
            pass
        if not class_:
            continue
        good_tag = False
        for pattern in PATTERNS:
            if pattern in class_:
                good_tag = True
        if good_tag is False:
            continue
        date_text = tag.string
        if date_text is None:
            date_text = tag.text
        possible_date = _parse_str_date(date_text, mine, maxe)
        if possible_date is not None:
            return possible_date

#     tag_id = [
#         # ('small', None),
#         ('div', None),
#     ]
#     for elem, eid in tag_id:
#         for tag in parsed_html.find_all([elem], id=eid):
#             candidate = _get_date_candidates(tag.text, mine, maxe)
#             if candidate:
#                 return candidate
#
#     return None
#
#
# def _get_date_candidates(string, mine, maxe):
#     pattern = re.compile('[0-9]+\.?.{2,10}[0-9]{2,4}')
#     for match in re.findall(pattern, string):
#         print(match)
#         if len(match) < 5:
#             continue
#         date = _parse_str_date(match, mine, maxe)
#         # if date:
#             # return date
#     return None


def extract_article_pubdate(uri, html, min_epoch=0, max_epoch=4102444800):
    """Try to extract the publish date from given URL/HTML content.

    By default allowed dates can range between 01.01.1970 and 01.01.2100.
    """
    if len(html) == 0:
        raise ValueError('Input HTML is empty')
    article_date = None
    date_hint = None
    # print(uri)
    try:
        # fallback
        url_date = _extract_from_url(uri, min_epoch, max_epoch)
        if url_date:
            date_hint = 'url'

        parsed_html = BeautifulSoup(html, 'html.parser')

        article_date, hint = _extract_from_ldjson(
            parsed_html, min_epoch, max_epoch)
        if article_date:
            return article_date, hint
        article_date, hint = _extract_from_meta(
            parsed_html, min_epoch, max_epoch)
        if article_date:
            return article_date, hint

        article_date = _extract_from_html_tag(
            parsed_html, min_epoch, max_epoch)
        if article_date:
            return article_date, 'html-tag'

        article_date = url_date

    except Exception as e:
        r_util.logerr(e)

    return article_date, date_hint


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
