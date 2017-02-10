def get_key_from_url(url):
    """Generates a filesafe perma-key from a given web url."""

    from re import sub
    from hashlib import md5
    key = sub('[^a-zA-Z0-9_-]', '_', url)
    key = sub('^http[s]?_', '', key)
    key = sub('^_+', '', key)
    key = sub('_+$', '', key)[:75]
    chksum = md5(url.encode('utf-8')).hexdigest()
    key = key + "_" + chksum
    return key
