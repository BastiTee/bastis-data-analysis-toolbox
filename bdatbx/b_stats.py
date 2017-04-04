"""Methods to gather statistics about the provided input data."""


def gather_basic_numerical_stats(array):
    """Calculate basic statistical values about a list of numerical values."""
    if array is None:
        array = []

    array = list(filter(None, array))

    _length = len(array)
    _sum = _min = _max = _mean = _stdev = _median = None

    # dont' work with non-numerical arrays
    is_numeric = False
    if _length > 0:
        try:
            float(array[0])
            is_numeric = True
        except ValueError:
            pass

    if _length > 0 and is_numeric:
        _sum = sum(array)
        _min = min(array)
        _max = max(array)

    if _length > 1 and is_numeric:
        from statistics import mean, stdev, median
        _mean = mean(array)
        _stdev = stdev(array, xbar=None)
        _median = median(array)

    return {
        'len': _length,
        'sum': _sum, 'min': _min, 'max': _max,
        'mean': _mean, 'stdev': _stdev, 'med': _median
    }
