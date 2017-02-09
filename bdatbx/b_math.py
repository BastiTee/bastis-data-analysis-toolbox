r"""Mathematics convenience functions."""


def round_ns(number, digits=0, default_return=None):
    """A wrapper for python's built-in round handling None-input."""

    if number is None:
        return default_return
    return round(number, digits)
