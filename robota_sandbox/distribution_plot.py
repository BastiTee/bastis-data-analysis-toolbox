#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tbd."""

from scipy import stats
from sys import exit
import seaborn as sns
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pandas as pd
from numpy.random import randint
import datetime as dt
import matplotlib.pyplot as plt
from robota import r_mongo, r_const


col = r_mongo.get_client_for_collection('bonndigital_2017-04-06.sanity')


def _print_df(df):
    print(df.head())
    print(df.describe())
    print(df.dtypes)
    print(df.index)
    print('--------')


dates = r_mongo.get_values_from_field_as_list(
    col, {r_const.DB_DATE_EP: {'$ne': None}}, [r_const.DB_DATE_EP],
    cast=lambda x: int(x))

pd.set_option('display.float_format', lambda x: '%i' % x)
df = pd.Series(dates)

_print_df(df)

df = df[abs(stats.zscore(df)) < 0.1]  # filter outlier
df = pd.to_datetime(df, unit='s')
df = df.apply(
    lambda df: datetime(year=df.year, month=df.month, day=df.day))
_print_df(df)


plt.setp(df.groupby(df.dt.year).count().plot(kind='bar'))
plt.show()

mind = datetime(2010, 1, 1)
resultsets = r_mongo.get_values_from_field_as_list(
    col, {'__date_humanread': {
        '$lt': mind}},
    [r_const.DB_SOURCE_URI, r_const.DB_DATE_HR, r_const.DB_DATE_HINT])
for resultset in resultsets:
    print('{}\t{}\t{}'.format(
        resultset[r_const.DB_DATE_HR],
        resultset[r_const.DB_DATE_HINT], resultset[r_const.DB_SOURCE_URI]))
