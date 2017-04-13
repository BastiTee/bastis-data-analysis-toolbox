# Notes

- All blog entries published in 2015.

```
{ "__date_humanread": { $gt: { $date: "2015-01-01T00:00:00.000Z" }, $lt: { $date: "2016-01-01T00:00:00.000Z" }}}
```

- All blog entries with a specific language.

```
{ "__lang_auto": "it" }
```

- All German blog entries in category "Bonn" with more than 500 tokens.

```
{"__lang_auto": {"$eq": "de"}, "__src_tags": {"$eq": ["Bonn"]}, "__te_tokencount": {"$gt": 500}}
```

- Regex Suche

```
{ "__dl_domain": { $regex: ".*rouge.*" } }
```

- Nicht-Null Suche

```
{ "__dl_error": { $ne: null } }
```
