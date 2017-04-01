r"""Sinmple database abstraction for mongo db"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError


def consolidate_mongo_key(col, key, if_filter=lambda x: True,
    process_value=lambda x: x):
    from re import sub
    from collections import Counter
    from bdatbx import b_stats
    cur = col.find({}, {key: 1, '_id': 0})
    resultset = [
        process_value(get_key_nullsafe(doc, key)) for doc in cur if if_filter(get_key_nullsafe(doc, key))]
    if len(resultset) > 0:
        # stringify lists
        if isinstance(resultset[0], list):
            resultset = [sub(']$', '', sub('^\[', '', str(result)))
                         for result in resultset]
    counter = Counter(resultset)
    resultset_stats = b_stats.gather_basic_numerical_stats(resultset)
    counter_stats = b_stats.gather_basic_numerical_stats(
        list(counter.values()))
    results = {
        'resultset': resultset,
        'resultset_len': len(resultset),
        'resultset_unique': len(set(resultset)),
        'resultset_none_vals': len([1 for val in resultset if val == None]),
        'counter': counter,
        'resultset_stats': resultset_stats,
        'counter_stats': counter_stats,
    }
    return results

def set_null_safe(doc, key, value):
    if doc is None or key is None:
        return
    doc[key] = value

def get_key_nullsafe(doc, key):
    if not doc or not key:
        return None
    try:
        return doc[key]
    except KeyError:
        return None


def update_value_nullsafe(col, doc, key, value=None):
    if col is None:
        return  # Bypass database on missing connectivity
    if doc is None:
        return
    if key is None:
        return
    doc[key] = value
    col.update_one({'_id': doc['_id']}, {'$set': {key: value}})


def get_snapshot_cursor(col, no_cursor_timeout=False):
    if col is None:
        return  # Bypass database on missing connectivity
    return col.find({}, modifiers={"$snapshot": True},
        no_cursor_timeout=no_cursor_timeout)


def get_doc_or_none(col, key, value):
    if col is None:
        return  # Bypass database on missing connectivity
    return col.find_one({key: value})


def has_doc(col, key, value):
    if col is None:
        return  # Bypass database on missing connectivity
    if col.find_one({key: value}):
        return True
    return False


def get_collection_size(col):
    if col is None:
        return  # Bypass database on missing connectivity
    return col.count()


def clear_collection(col):
    if col is None:
        return  # Bypass database on missing connectivity
    result = col.delete_many({})


def delete_doc(col, doc):
    if col is None:
        return  # Bypass database on missing connectivity
    result = col.delete_one({'_id': doc['_id']})


def insert_doc(col, doc):
    if col is None:
        return  # Bypass database on missing connectivity
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        pass


def replace_doc(col, doc):
    if col is None:
        return  # Bypass database on missing connectivity
    col.replace_one({'_id': doc['_id']}, doc)


def change_id(col, doc, new_id):
    if col is None:
        return  # Bypass database on missing connectivity
    old_id = doc['_id']
    doc = col.find_one({'_id': old_id})
    doc['_id'] = new_id
    res = col.delete_one({'_id': old_id})
    col.insert_one(doc)
    return doc


def get_client_for_collection(col_name, create=True):
    from bdatbx import b_util
    client = MongoClient()
    try:
        client.admin.command('ismaster')
    except ConnectionFailure:
        b_util.logerr('Mongodb server not available!')
        return None
    db = client.bdatbx
    if not col_name in db.collection_names() and not create:
        b_util.logerr('Collection not present and create-option is disabled.')
        return None
    col = db[col_name]
    return col
