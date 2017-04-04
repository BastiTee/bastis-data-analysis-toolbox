#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runs a single request to a webpage."""

import sys
import requests
from requests import exceptions

try:
    url = sys.argv[1]
except IndexError:
    print('No URL provided.')
    sys.exit(1)

print('\n--- {}\n'.format(url))

try:
    s = requests.Session()
    print('{}\n'.format(s.headers))
    r = s.get(url)
except exceptions.TooManyRedirects as t:
    print('ERROR: {}'.format(t))
    r = s.get(url, allow_redirects=False)

print('-----------------------------')
print(r.status_code)
print(r.headers)
