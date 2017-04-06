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


def _parse_str_date(date_string):
    try:
        date_time_obj = parse(date_string)
        # print('>>> {}'.format(date_time_obj))
        return date_time_obj
    except Exception as e:
        # print('ERR >> {}'.format(e))
        return None


def _extract_from_url(url):

    matcher = re.search(
        r'([\./\-_]{0,1}(19|20)\d{2})[\./\-_]{0,1}(([0-3]{0,1}[0-9]' +
        '[\./\-_])|(\w{3,5}[\./\-_]))([0-3]{0,1}[0-9][\./\-]{0,1})?', url)
    if matcher:
        return _parse_str_date(matcher.group(0))

    return None


def _extract_from_ldjson(parsed_html):
    json_date = None
    try:
        script = parsed_html.find('script', type='application/ld+json')
        if script is None:
            return None

        data = json.loads(script.text)

        try:
            json_date = _parse_str_date(data['datePublished'])
        except Exception as e:
            pass

        try:
            json_date = _parse_str_date(data['dateCreated'])
        except Exception as e:
            pass

    except Exception as e:
        return None

    return json_date


def _extract_from_meta(parsed_html):

    for meta_element in parsed_html.findAll('meta'):
        meta_content = meta_element.get('content', '')
        if not meta_content or len(meta_content) < 4 or len(meta_content) > 50:
            continue
        meta_cand = [meta_element.get(hint) for hint in [
            'name', 'property', 'itemprop', 'http-equiv']
            if meta_element.get(hint, None)]

        for label in ['publish', 'date', 'created', 'time']:
            if label in meta_cand:
                dt = _parse_str_date(meta_element['content'].strip())
                if dt:
                    return dt
    return None


def _extract_from_html_tag(parsed_html):
    # <time>
    for time in parsed_html.findAll('time'):
        datetime = time.get('datetime', '')
        if len(datetime) > 0:
            de = _parse_str_date(datetime)
            if de:
                return de

        datetime = time.get('class', '')
        if len(datetime) > 0 and datetime[0].lower() == 'timestamp':
            de = _parse_str_date(time.string)
            if de:
                return de

        datetext = _parse_str_date(time.text)
        if datetext:
            return datetext
    tag = parsed_html.find('span', {'itemprop': 'datePublished'})
    if tag is not None:
        date_text = tag.get('content')
        if date_text is None:
            date_text = tag.text
        if date_text is not None:
            return _parse_str_date(date_text)

    # class=
    # re.compile(
    # 'pubdate|timestamp|post-date|date-header|' +
    #     'article_date|articledate|date'
    elements = ['abbr', 'span', 'p', 'div', 'h1', 'h2', 'h3', 'li']
    classes = [
        'blogheader', 'pubdate', 'published', 'timestamp', 'post-date',
        'date-header', 'article_date', 'articledate', 'date',
        'content-column', 'one_half', 'theTime']
    for class_ in classes:
        for tag in parsed_html.find_all(elements, class_=class_):
            date_text = tag.string
            # print(date_text)
            if date_text is None:
                date_text = tag.text

            possible_date = _parse_str_date(date_text)

            if possible_date is not None:
                return possible_date

    tag_id = [
        ('small', None),
        ('div', None),
    ]
    for elem, eid in tag_id:
        for tag in parsed_html.find_all([elem], id=eid):
            candidate = _get_date_candidates(tag.text)
            if candidate:
                return candidate

    return None


def _get_date_candidates(string):
    pattern = re.compile('[0-9]+\.?.{2,10}[0-9]{2,4}')
    for match in re.findall(pattern, string):
        if len(match) < 5:
            continue
        date = _parse_str_date(match)
        if date:
            return date
    return None


def extract_article_pubdate(article_link, html):
    """Try to extract the publish date from given URL/HTML content."""
    article_date = None
    date_hint = None

    try:
        # fallback
        url_date = _extract_from_url(article_link)
        if url_date:
            date_hint = 'url'

        parsed_html = BeautifulSoup(html, 'html.parser')

        article_date = _extract_from_ldjson(parsed_html)
        if article_date:
            return article_date, 'json-ld'

        article_date = _extract_from_meta(parsed_html)
        if article_date:
            return article_date, 'meta'

        article_date = _extract_from_html_tag(parsed_html)
        if article_date:
            return article_date, 'html-tag'

        article_date = url_date

    except Exception as e:
        r_util.logerr(e)

    return article_date, date_hint


if __name__ == '__main__':
    import requests
    import sys
    try:
        url = sys.argv[1]
    except IndexError:
        print('No URL provided')
        sys.exit(1)
    html = requests.get(url, timeout=10).text
    date, hint = extract_article_pubdate(url, html)
    if not hint:
        hint = '??'
    if not date:
        date = '??'
    print('{} | {} | {}'.format(hint.ljust(8), str(date).ljust(25), url[:80]))
