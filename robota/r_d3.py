"""Helper methods to prepare d3.js visualization."""


def breadcrumbs_to_json_hierarchy(array, count_leafs_only=True,
                                  remove_zeros=True, minimum_leaf_size=0):
    """tbd."""
    from collections import Counter
    # filter by minimum leaf size
    if minimum_leaf_size > 0:
        keys = []
        for row in array:
            keys.append('_'.join(row))
        ct = Counter(keys)
        array = [row for row in array if ct['_'.join(row)] > minimum_leaf_size]
    # get row with most elements
    max_dims = max([len(row) for row in array])
    # if first dimension has only one unique value, use it as root
    uniq_vals_first_dim = set([row[0] for row in array])
    has_root = len(uniq_vals_first_dim) == 1
    # setup final object
    root = {
        'name': list(uniq_vals_first_dim)[0] if has_root else 'root',
        'size': 0,
        'children': []
    }
    # create tree and count leafs
    start = 1 if has_root else 0
    for row in array:
        node = root
        for i in range(start, len(row)):
            leaf = i == len(row) - 1
            child = _get_child_with_name(node['children'], row[i])
            if not child:
                child = {
                    'name': row[i],
                    'size': 1 if leaf else 0,
                    'children': []
                }
                node['children'].append(child)
            elif leaf:
                child['size'] = child['size'] + 1
            node = child
    # go through tree and count cumulative values
    _recurse_count_values(root, count_leafs_only)
    # clean up empty arrays and zero-counts
    if remove_zeros:
        _recurse_cleanup(root)
    return root


def _recurse_cleanup(node):
    for child in node['children']:
        _recurse_cleanup(child)
    if node['size'] == 0:
        del node['size']
    if len(node['children']) == 0:
        del node['children']


def _has_uncounted_children(node):
    for child in node['children']:
        if child['size'] == 0:
            return True
    return False


def _recurse_count_values(node, count_leafs_only):
    if _has_uncounted_children(node):
        for child in node['children']:
            _recurse_count_values(child, count_leafs_only)
    if count_leafs_only and len(node['children']) > 0:
        return
    node['size'] = sum([child['size'] for child in node['children']])


def _get_child_with_name(childs, name):
    for child in childs:
        if child['name'] == name:
            return child
    return None
