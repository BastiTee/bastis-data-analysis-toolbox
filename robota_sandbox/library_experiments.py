#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TBD."""
# import newspaper
#
# input_src = 'https://www.hagen-bauer.de/'
# cnn_paper = newspaper.build(input_src)
# print('>' + str(len(cnn_paper.articles)))
# for article in cnn_paper.articles:
#     print(article.url)
#
# for category in cnn_paper.category_urls():
#     print(category)
#
import requests
from readability import Document
# readability-lxml

response = requests.get(
    'http://www.zeit.de/zeit-magazin/2017/15/leslie-feist-saengerin-kanada')
doc = Document(response.text)
print(doc.title())
print(doc.short_title())
print(doc.summary())
