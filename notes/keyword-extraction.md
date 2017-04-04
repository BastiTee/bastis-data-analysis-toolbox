# Keyword extraction

## Command lines

```shell
python3 -m bdatbx_scripts.get-keywords -i ../bonnerblogs-analysis/_bonndigital_2016-11-06.full-plain-text/ -c bonndigital_2016-11-06.full -n nltk-data/
```

## Queries

```json
{"__lang_auto": {"$eq": "de"}, "__src_tags": {"$eq": ["Bonn"]}, "__te_tokencount": {"$gt": 500}}
```
