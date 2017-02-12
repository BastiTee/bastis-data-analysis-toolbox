#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------------------ CMD-LINE-PARSING
from bdatbx import b_cmdprs
prs = b_cmdprs.init('Generate basic token statistics')
b_cmdprs.add_dir_in(prs)
b_cmdprs.add_dir_out(prs)
b_cmdprs.add_verbose(prs)
args = prs.parse_args()
b_cmdprs.check_dir_in(prs, args)
b_cmdprs.check_dir_out_and_chdir(prs, args)
# -----------------------------------------------------------------------------

from bptbx import b_iotools

# CURRENT FORMAT:
#  [0] - Generated permakey
#  [1] - Source permalink
#  [2] - HTTP response code
#  [3] - Path to downloaded raw text data
#  [4] - Raw text data file size in bytes
#  [5] - Estimated content language
#  [6] - Total number of tokens
#  [7] - Total number of stemmed and stopword-cleared tokens
#  [8] - Path to tokenized text data
#
# total_usable=0
# total_de=0
# total_en=0
# min_tokens=None
# max_tokens=None
# total_tokens=None
# avg_tokens=None
# for d in plain_datasets:
#     if d[2] != '200' or not d[7] or not int(d[7]) > 10:
#         continue
#     total_usable += 1
#     if d[5] == 'en':
#         total_en += 1
#     else:
#         total_de += 1
#     if total_usable == 1:
#         min_tokens=max_tokens=avg_tokens=total_tokens=int(d[7])
#     else:
#         min_tokens=min(min_tokens, int(d[7]))
#         max_tokens=max(max_tokens, int(d[7]))
#         total_tokens += int(d[7])
#         avg_tokens=total_tokens / total_usable
#
#
# print('-- datasets')
# print('   + total:    {}'.format(len(plain_datasets)))
# print('   + usable:   {}'.format(total_usable))
# print('   + german:   {}'.format(total_de))
# print('   + english:  {}'.format(total_en))
# print('-- tokens')
# print('   + total:    {}'.format(total_tokens))
# print('   + min:      {}'.format(min_tokens))
# print('   + max:      {}'.format(max_tokens))
# print('   + avg:      {}'.format(int(avg_tokens)))


def main():
    pass
