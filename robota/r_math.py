"""Mathematics convenience functions."""


def round_ns(number, digits=0, default_return=None):
    """A wrapper for python's built-in round handling None-input."""
    if number is None:
        return default_return
    return round(number, digits)


def count_and_sort(array, reverse=False, remove_outliers=False):
    """Count the elements in the given array and sort by element."""
    amap = {}
    for el in array:
        try:
            amap[el]
        except KeyError:
            amap[el] = 0
        amap[el] = amap[el] + 1

    rej = _reject_outliers(list(amap.values()))
    rejmin = min(rej)
    rejmax = max(rej)
    new_array = []
    for sorted_key in sorted(amap.keys(), reverse=reverse):
        count = amap[sorted_key]
        if count < rejmin or count > rejmax:
            continue
        new_array.append([sorted_key, amap[sorted_key]])

    return new_array


def _reject_outliers(arr, m=2):
    import numpy
    elements = numpy.array(arr)

    mean = numpy.mean(elements, axis=0)
    sd = numpy.std(elements, axis=0)

    final_list = [x for x in arr if (x > mean - m * sd)]
    final_list = [x for x in final_list if (x < mean + m * sd)]
    return final_list
