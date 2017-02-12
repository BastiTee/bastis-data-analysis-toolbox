r"""Processing utilities."""


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


def log(message, stack_back=0, color='0;33;40'):
    if not message or message is None:
        return
    # find out what module called the logging
    mod = get_calling_module(stack_back + 1)
    from re import sub
    mod = sub('_+', ' ', sub('.py$', '', mod))
    ccase = ''
    for i in mod.upper().split():
        ccase += i[0]
    ccase = '[{}]'.format(ccase)
    # print with given suffix and colors
    print('\x1b[{}m{} {}\x1b[0m'.format(color, ccase, message))


def get_calling_module(stack_back=0):
    # find out what module called the logging
    from inspect import stack, getmodule
    mod = getmodule(stack()[1 + stack_back][0]).__file__
    from os import path
    mod = path.basename(mod)
    return mod


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


def object_to_json(obj):
    import json
    json_string = json.dumps(obj, default=_internal_to_json)
    return json_string


def _internal_to_json(object):
    if isinstance(python_object, time.struct_time):
        return {'__class__': 'time.asctime',
                '__value__': time.asctime(python_object)}

    raise TypeError(repr(python_object) + ' is not JSON serializable')


def json_to_object(json_string):
    import json
    obj = json.loads(json_string)
    return obj


if __name__ == '__main__':
    obj = {'foo': 123}
    json_string = object_to_json(obj)
    obj_back = json_to_object(json_string)
    assert obj == obj_back
