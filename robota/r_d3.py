"""Helper methods to prepare d3.js visualization."""

from collections import Counter


def _get_child_with_name(childs, name):
    for child in childs:
        if child['name'] == name:
            return child
    return None


def _has_uncounted_children(node):
    for child in node['children']:
        if child['value'] == 0:
            return True
    return False


def _recurse_count_values(node):
    if _has_uncounted_children(node):
        for child in node['children']:
            _recurse_count_values(child)
    node['value'] = sum([child['value'] for child in node['children']])


def breadcrumbs_to_json_hierarchy(array):
    """Convert."""
    # get row with most elements
    max_dims = max([len(row) for row in array])
    # if first dimension has only one unique value, use it as root
    uniq_vals_first_dim = set([row[0] for row in array])
    has_root = len(uniq_vals_first_dim) == 1
    # setup final object
    root = {
        "name": list(uniq_vals_first_dim)[0] if has_root else "root",
        "value": 0,
        "children": []
    }
    # first pass: create tree and count leafs
    start = 1 if has_root else 0
    for row in array:
        node = root
        for i in range(start, len(row)):
            leaf = i == len(row) - 1
            child = _get_child_with_name(node['children'], row[i])
            if not child:
                child = {
                    "name": row[i],
                    "value": 1 if leaf else 0,
                    "children": []
                }
                node['children'].append(child)
            elif leaf:
                child['value'] = child['value'] + 1
            node = child
    # second pass: go through tree and count cumulative values
    _recurse_count_values(root)
    return root
