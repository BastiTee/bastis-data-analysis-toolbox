#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Installs NLTK environment at current location."""

import nltk
from sys import argv

default_modules = [
    'averaged_perceptron_tagger',
    'stopwords',
    'punkt'
    ]
add_modules = argv[1:]
modules = default_modules + add_modules

for module in modules:
    print('-- installing \'{}\''.format(module))
    nltk.download(module, download_dir='nltk-data')
