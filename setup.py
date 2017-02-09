#!/usr/bin/env python3

from setuptools import setup
from os import path, listdir, chdir, getcwd
from re import sub

chdir(path.dirname(path.abspath(__file__)))

script_folder = 'bdatbx_scripts'
scripts = []
for fname in listdir(script_folder):
    fabs = path.abspath(path.join(script_folder, fname))
    if (
        not '__init__' in fabs and
        not '.pyc' in fabs and
        not path.isdir(fabs)
    ):
        script_n = sub('\.py$', '', fname)
        script_bin = sub('_', '-', script_n)
        scripts.append('bdatbx-{} = {}.{}:main'.format(
            script_bin, script_folder, script_n))

setup(
    name='bdatbx',
    version='0.1.0',
    description='''Basti\'s Data Analysis Toolbox.''',
    long_description='''Mostly python-based library and scripts to analyse data.''',
    author='Basti Tee',
    author_email='basti.tee@gmx.de',
    url='tbd',
    packages=['bdatbx', 'bdatbx_scripts'],
    package_data={'bdatbx': ['resource']},
    install_requires=[],
    entry_points={
        'console_scripts': scripts,
    },
    zip_safe=False,
)
