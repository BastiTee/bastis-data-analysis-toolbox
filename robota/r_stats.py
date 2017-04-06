"""Methods to gather statistics about the provided input data."""


def gather_basic_numerical_stats(array):
    """Calculate basic statistical values about a list of numerical values."""
    if array is None:
        array = []

    array = list(filter(None, array))

    _length = len(array)
    _sum = _min = _max = _mean = _stdev = _median = _error = None

    try:
        # make sure only numeric values in array
        array = [int(elem) for elem in array if elem]

        if _length > 0:
            _sum = sum(array)
            _min = min(array)
            _max = max(array)

        if _length > 1:
            from statistics import mean, stdev, median
            _mean = mean(array)
            _stdev = stdev(array, xbar=None)
            _median = median(array)

    except Exception as e:
        _error = e
    finally:
        return {
            '_error': _error,
            'len': _length,
            'sum': _sum, 'min': _min, 'max': _max,
            'mean': _mean, 'stdev': _stdev, 'med': _median
        }
