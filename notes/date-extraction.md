# Date extraction

## Sanity analysis

- Knows issues

  - No multi-threading mode possible (weird concurrency issues)

### Testruns on sanity

```
rm -f _testrun.txt && export PYTHONPATH=${PYTHONPATH}:_robota_install && \
time python3 -m robota_scripts.extract_pubdate_from_html \
-i _bonndigital_2017-04-06.sanity-raw-html/ -c bonndigital_2017-04-06.sanity \
-o _testrun.txt -t1
```

- Baseline

```
Git 17338c913d6744efbee94360d545ca4dbf25fee5
190291179605.00 max / -13837740808.00 min
837 tot / 415 uniq / 92 none
+-----+---------------+
| 695 | html-tag      |
|  92 | -             |
|  28 | json-ld       |
|  17 | url           |
|   5 | meta-['date'] |
+-----+---------------+
real    2m38.123s
user    2m37.248s
sys    0m0.208s
```

- Meta-extraction fixed

```
+-----------+-----+
| total     | 837 |
| none_vals |  87 |
+-----------+-----+
+-----+----------+
| 449 | meta     |
| 256 | html-tag |
|  87 | -        |
|  28 | json-ld  |
|  17 | url      |
+-----+----------+
real    2m49.448s
user    2m48.628s
sys    0m0.228s
```

- Refactored and generalized ld-json extraction

```
+-----------+-----+
| total     | 837 |
| unique    |   5 |
| none_vals |  87 |
+-----------+-----+
+-----+----------+
| 449 | meta     |
| 256 | html-tag |
|  87 | -        |
|  28 | json-ld  |
|  17 | url      |
+-----+----------+
real    2m50.822s
user    2m50.252s
sys    0m0.212s
```

- Added more input validation and cleaning on parser method

```
+--------+------------------+
| stdev  |      43222666.07 |
| mean   |    1456254245.07 |
| _error |                  |
| len    |           749.00 |
| min    |     956008800.00 |
| sum    | 1090734429556.00 |
| med    |    1452207600.00 |
| max    |    2061496800.00 |
+--------+------------------+
+-----------+-----+
| total     | 837 |
| unique    |   5 |
| none_vals |  88 |
+-----------+-----+
+-----+----------+
| 449 | meta     |
| 255 | html-tag |
|  88 | -        |
|  28 | json-ld  |
|  17 | url      |
+-----+----------+
real    2m4.558s
user    2m3.872s
sys    0m0.244s
```

- Optimized html tag extraction (removed broad scan, generalized tag search) --> Outliers are gone now.

```
+-----------+-----+
| total     | 837 |
| unique    |   5 |
| none_vals | 143 |
+-----------+-----+
+-----+----------+
| 449 | meta     |
| 202 | html-tag |
| 143 | -        |
|  28 | json-ld  |
|  15 | url      |
+-----+----------+
user    1m46.216s
sys    0m0.212s
```
