"""Mathematics convenience functions."""


def is_number(candidate):
    """Return true if given candidate string is a number."""
    try:
        float(candidate)
        return True
    except ValueError:
        return False


def round_ns(number, digits=0, default_return=None):
    """A wrapper for python's built-in round handling None-input."""
    if number is None:
        return default_return
    return round(number, digits)


def count_and_sort(array, reverse=False, reject_outliers=False, outliers_m=2):
    """Count the elements in the given array and sort by element."""
    amap = {}
    for el in array:
        try:
            amap[el]
        except KeyError:
            amap[el] = 0
        amap[el] = amap[el] + 1

    rej = _reject_outliers(list(amap.values()), m=outliers_m)
    rejmin = min(rej)
    rejmax = max(rej)
    new_array = []
    for sorted_key in sorted(amap.keys(), reverse=reverse):
        count = amap[sorted_key]
        if (count < rejmin or count > rejmax) and reject_outliers:
            continue
        new_array.append([sorted_key, amap[sorted_key]])

    return new_array


def get_minimum_levenshtein_distance(string_a_list, string_b):
    """Return the minimum levenshtein distance for a list of strings.

    This will return the minimum levenshtein distance and a list of strings
    out of string_a_list that have this edit distance to string_b.
    """
    if not string_a_list:
        raise ValueError('string_a_list was None')
    if len(string_a_list) < 1:
        raise ValueError('string_a_list was empty')
    if not string_b or len(string_b) < 1:
        raise ValueError('string_b was empty')
    pre_results = []
    for i, string_a in enumerate(string_a_list):
        ed = get_levenshtein_distance(string_a, string_b)
        pre_results.append([string_a, ed, i])
    pre_results.sort(key=lambda x: x[1])
    min_dist = pre_results[0][1]
    result_list = [result[0] for result in pre_results
                   if result[1] <= min_dist]
    result_idx = [result[2] for result in pre_results
                  if result[1] <= min_dist]
    # print('')
    # print('min-dist =', min_dist)
    # print('pre-resu =', pre_results)
    # print('results  =', result_list)

    # list = [ 'foo', 'bar', 'tar', 'barfoo', 'foobar', 'toobar']
    # print(r_math.get_minimum_levenshtein_distance(list, 'foo'))
    # print(r_math.get_minimum_levenshtein_distance(list, 'fooba'))
    # print(r_math.get_minimum_levenshtein_distance(list, 'oobar'))
    # print(r_math.get_minimum_levenshtein_distance(list, 'foobar'))
    # print(r_math.get_minimum_levenshtein_distance(list, 'oob'))

    return min_dist, result_list, result_idx


def get_levenshtein_distance(string_a, string_b):
    """Return the edit distance of the two given strings."""

    import editdistance
    return editdistance.eval(string_a, string_b)


def _reject_outliers(arr, m=2):
    import numpy
    elements = numpy.array(arr)

    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    final_list = [x for x in arr if (x > mean - m * sd)]
    final_list = [x for x in final_list if (x < mean + m * sd)]
    return final_list
