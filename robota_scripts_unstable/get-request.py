#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runs a single GET request to a given URL."""

from sys import argv, exit, stderr
from requests import exceptions, Session as sess

try:
    url = argv[1]
except IndexError:
    print('No URL provided.')
    exit(1)

print('URL={}'.format(url), file=stderr)

try:
    s = sess()
    print('REQUEST-HEADERS={}'.format(s.headers), file=stderr)
    r = s.get(url)
except exceptions.TooManyRedirects as t:
    print('ERROR={}'.format(t), file=stderr)
    r = s.get(url, allow_redirects=False)

print("STATUS={}".format(r.status_code), file=stderr)
print("RESPONSE-HEADERS={}".format(r.headers), file=stderr)
print(r.text)

