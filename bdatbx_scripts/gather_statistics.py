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
from bdatbx import b_util

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
# b_util.log('-- datasets')
# b_util.log('   + total:    {}'.format(len(plain_datasets)))
# b_util.log('   + usable:   {}'.format(total_usable))
# b_util.log('   + german:   {}'.format(total_de))
# b_util.log('   + english:  {}'.format(total_en))
# b_util.log('-- tokens')
# b_util.log('   + total:    {}'.format(total_tokens))
# b_util.log('   + min:      {}'.format(min_tokens))
# b_util.log('   + max:      {}'.format(max_tokens))
# b_util.log('   + avg:      {}'.format(int(avg_tokens)))


def main():
    pass
