r"""Methods to gather statistics about the provided input data."""


def gather_basic_numerical_stats(array):
    r"""Calculate basic statistical values about a list of
    numerical values."""

    if array is None:
        array = []

    _length = _sum = _min = _max = _mean = _stdev = _median = None

    _length = len(array)
    if _length > 0:
        _sum = sum(array)
        _min = min(array)
        _max = max(array)

    if _length > 1:
        from statistics import mean, stdev, median
        _mean = mean(array)
        _stdev = stdev(array, xbar=None)
        _median = median(array)
        
    return {
        'len': _length, 'sum': _sum, 'min': _min, 'max': _max,
        'mean': _mean, 'stdev': _stdev, 'med': _median
    }
