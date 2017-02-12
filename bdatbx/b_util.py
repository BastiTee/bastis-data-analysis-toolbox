def get_key_from_url(url):
    """Generates a filesafe permakey from a given input url."""

    from re import sub
    from hashlib import md5
    file_key = sub('[^a-zA-Z0-9_-]', '_', url)
    file_key = sub('^http[s]?_', '', file_key)
    file_key = sub('^_+', '', file_key)
    file_key = sub('_+$', '', file_key)[:75]
    chksum = md5(url.encode('utf-8')).hexdigest()
    file_key = file_key + '_' + chksum
    dir_key = file_key[:16]
    return file_key, dir_key


def setup_progressbar(item_count):
    import progressbar
    from threading import Lock
    global p_bar, p_pointer, p_lock
    p_bar = progressbar.ProgressBar(max_value=item_count)
    p_pointer = 0
    p_lock = Lock()


def update_progressbar():
    global p_bar, p_pointer, p_lock
    with p_lock:
        if not p_bar:
            return
        p_pointer += 1
        p_bar.update(p_pointer)


def finish_progressbar():
    global p_bar, p_pointer, p_lock
    if p_bar:
        p_bar.finish()
