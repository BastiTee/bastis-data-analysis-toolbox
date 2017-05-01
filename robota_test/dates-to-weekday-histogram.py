#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TPD."""

# import fileinput
import sys
from bptbx import b_date

res_map = {}

for line in sys.stdin:
    if not line:
        continue
    line = line.strip()
    try:
        dto = b_date.timestamp_to_dto(line, "%Y%m%d-%H%M%S")
    except ValueError:
        # skip invalid datetimes
        continue
    weekday = int(dto.strftime('%w'))
    if weekday == 0:  # make sunday the 7th day like jebuz would
        weekday = 7
    try:
        res_map[weekday]
    except KeyError:
        res_map[weekday] = {
            '00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0,
            '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
            '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0,
            '18': 0, '19': 0, '20': 0, '21': 0, '22': 0, '23': 0,
        }
    # if dto.strftime("%H") == "00":
    #     hourofday = "24"
    # else:
    hourofday = dto.strftime("%H")
    curr_val = res_map[weekday][hourofday]
    res_map[weekday][hourofday] = curr_val + 1

print('day,hour,value')
for key in res_map.keys():
    vals = sorted(list(res_map[key].keys()))
    for val in vals:
        print('{},{},{}'.format(key, val, res_map[key][val]))
