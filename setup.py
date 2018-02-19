#!/usr/bin/env python3
"""Setup script."""

from setuptools import setup
from os import path, listdir, chdir
from re import sub

chdir(path.dirname(path.abspath(__file__)))

script_folder = 'robota_scripts'
scripts = []
for fname in listdir(script_folder):
    fabs = path.abspath(path.join(script_folder, fname))
    if (
        '__init__' not in fabs and
        '.pyc' not in fabs and
        not path.isdir(fabs)
    ):
        script_n = sub('\.py$', '', fname)
        script_bin = sub('_', '-', script_n)
        scripts.append('robota-{} = {}.{}:main'.format(
            script_bin, script_folder, script_n))

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
    entry_points={
        'console_scripts': scripts,
    },
    zip_safe=False,
)
