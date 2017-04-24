"""Simple database abstraction for MongoDB."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError


def consolidate_mongo_key(col, key, if_filter=lambda x: True,
                          process_value=lambda x: x):
    """Read a specific key from DB for all docs and create statistics."""
    from re import sub
    from collections import Counter
    from robota import r_stats
    cur = col.find({}, {key: 1, '_id': 0})
    resultset = [
        process_value(get_key_nullsafe(doc, key))
        for doc in cur if if_filter(get_key_nullsafe(doc, key))]
    if len(resultset) > 0:
        # stringify lists
        if isinstance(resultset[0], list):
            resultset = [sub(']$', '', sub('^\[', '', str(result)))
                         for result in resultset]
    # print(resultset)
    counter = Counter(resultset)
    resultset_stats = r_stats.gather_basic_numerical_stats(resultset)
    # print(resultset_stats)
    counter_stats = r_stats.gather_basic_numerical_stats(
        list(counter.values()))
    results = {
        'resultset': resultset,
        'resultset_len': len(resultset),
        'resultset_unique': len(set(resultset)),
        'resultset_none_vals': len([1 for val in resultset if val is None]),
        'counter': counter,
        'resultset_stats': resultset_stats,
        'counter_stats': counter_stats,
    }
    return results


def set_null_safe(doc, key, value):
    """Set a value to a document after checking for None-values."""
    if doc is None or key is None:
        return
    doc[key] = value


def get_key_nullsafe(doc, key):
    """Return a value from a document after checking for None-values."""
    if not doc or not key:
        return None
    try:
        return doc[key]
    except KeyError:
        return None


def update_value_nullsafe(col, doc, key, value=None):
    """Update a document value in DB after checking for None-values."""
    if col is None:
        return  # Bypass database on missing connectivity
    if doc is None:
        return
    if key is None:
        return
    doc[key] = value
    col.update_one({'_id': doc['_id']}, {'$set': {key: value}})


def get_snapshot_cursor(col, no_cursor_timeout=False):
    """Return a cursor for all documents in collection."""
    if col is None:
        return  # Bypass database on missing connectivity
    return col.find({}, modifiers={"$snapshot": True},
                    no_cursor_timeout=no_cursor_timeout)


def find_docs(col, query, no_cursor_timeout=False):
    """Return a cursor for the given query."""
    if col is None:
        return  # Bypass database on missing connectivity
    return col.find(query, modifiers={"$snapshot": True},
                    no_cursor_timeout=no_cursor_timeout)


def get_doc_or_none(col, key, value):
    """Return the first document from DB having the given key/value pair."""
    if col is None:
        return  # Bypass database on missing connectivity
    return col.find_one({key: value})


def has_doc(col, key, value):
    """Check if a document exists in DB having the given key/value pair."""
    if col is None:
        return  # Bypass database on missing connectivity
    if col.find_one({key: value}):
        return True
    return False


def get_values_from_field_as_list(col, query, fields=[], cast=lambda x: x):
    """Return values from a single field as list."""
    if col is None:
        return  # Bypass database on missing connectivity

    field_filter = {'_id': 0}
    for field in fields:
        field_filter[field] = 1
    cursor = col.find(query, field_filter, modifiers={"$snapshot": True})
    if len(fields) == 1:
        mylist = [list(doc.values()) for doc in cursor]
        mylist = [cast(item) for sublist in mylist for item in sublist]
    else:
        mylist = [doc for doc in cursor]
    return mylist


def get_collection_size(col):
    """Return size of collection."""
    if col is None:
        return  # Bypass database on missing connectivity
    return col.count()


def count_docs(col, query):
    """Return size of collection for given query."""
    if col is None:
        return  # Bypass database on missing connectivity
    return col.count(query)


def clear_collection(col):
    """Delete all documents from collection."""
    if col is None:
        return  # Bypass database on missing connectivity
    col.delete_many({})


def delete_doc(col, doc):
    """Delete the given document from DB."""
    if col is None:
        return  # Bypass database on missing connectivity
    col.delete_one({'_id': doc['_id']})


def add_doc(col, doc):
    """Add the given document to DB."""
    insert_doc(col, doc)


def insert_doc(col, doc):
    """Insert the given document to DB."""
    if col is None:
        return  # Bypass database on missing connectivity
    try:
        col.insert_one(doc)
    except DuplicateKeyError:
        pass


def replace_doc(col, doc):
    """Replace the given document in DB."""
    if col is None:
        return  # Bypass database on missing connectivity
    col.replace_one({'_id': doc['_id']}, doc)


def change_id(col, doc, new_id):
    """Change the ID of a given document in DB."""
    if col is None:
        return  # Bypass database on missing connectivity
    old_id = doc['_id']
    doc = col.find_one({'_id': old_id})
    doc['_id'] = new_id
    col.delete_one({'_id': old_id})
    col.insert_one(doc)
    return doc


def get_client_for_collection(col_name, create=True):
    """Return a client for the given collection. Create it if wanted."""
    from robota import r_util
    client = MongoClient()
    try:
        client.admin.command('ismaster')
    except ConnectionFailure:
        r_util.logerr('Mongodb server not available!')
        return None
    db = client.robota
    if col_name not in db.collection_names() and not create:
        r_util.logerr('Collection not present and create-option is disabled.')
        return None
    col = db[col_name]
    return col
