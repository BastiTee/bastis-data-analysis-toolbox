r"""Utility belt to parse, match or convert recurring data formats."""


def parse_basic_money_format_to_float(amount):
    """Converts the basic money format, e.g., '-1.000,00' or '123.32'
    to a float value."""

    if amount is None:
        raise ValueError('Amount cannot be None')
    from re import match, sub
    valid_format = match('-?[0-9\.]+,[0-9]{2}', amount)
    if valid_format is None:
        raise ValueError(
            'Money amount does not match format \'-?[0-9\.]+,[0-9]{2}\'')
    amount = sub('\.', '', amount)
    amount = sub(',', '.', amount)
    amount = float(amount)
    return amount


def contains(pattern, string):
    """A convenience function to quickly test if a string
    contains a pattern."""
    if pattern is None:
        raise ValueError('Pattern cannot be None')
    if string is None:
        return False
    from re import match, IGNORECASE
    if match('.*{}.*'.format(pattern), string, IGNORECASE):
        return True
    return False
