#!/usr/bin/env python3
"""Setup script."""

from setuptools import setup
from os import path, listdir, chdir
from re import sub

setup(
    name='robota',
    version='0.1.0',
    description='''Yet another Python data analysis tool belt.''',
    long_description='''Yet another Python data analysis tool belt.''',
    author='Basti Tee',
    author_email='basti.tee@posteo.de',
    url='tbd',
    packages=['robota', 'robota_scripts'],
    package_data={'robota': ['resource/*']},
    install_requires=[],
    zip_safe=False,
)
