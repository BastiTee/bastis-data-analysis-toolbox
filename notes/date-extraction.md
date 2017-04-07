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
837 tot / 415 uniq / 92 none
190291179605.00 max / -13837740808.00 min
real    2m38.123s
user    2m37.248s
sys    0m0.208s
```
