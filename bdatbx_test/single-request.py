#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import requests
from requests import exceptions

try:
    url=sys.argv[1]
except IndexError:
    print('No URL provided.')
    sys.exit(1)

print('\n--- {}\n'.format(url))

try:
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36'
    print('{}\n'.format(s.headers))
    r = s.get(url)
except exceptions.TooManyRedirects as t:
    print('ERROR: {}'.format(t))
    r = s.get(url, allow_redirects=False)

print('-----------------------------')
print(r.status_code)
print(r.headers)
