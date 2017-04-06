"""Processing utilities."""

#############################################################################
# PRINTING OF RESULTSETS
#############################################################################


def print_result_statistics(results, label, print_counter=True,
                            counter_max=None,
                            print_resultset_stats=False,
                            print_counter_stats=False):
    """Print a result set."""
    log('\n+++ {} +++'.format(label.upper()), color='green')

    log('\nOVERVIEW')
    t = [
        ['total', results['resultset_len']],
        ['unique', results['resultset_unique']],
        ['none_vals', results['resultset_none_vals']],
    ]
    _print_table(t)

    if print_counter:
        log('\nCOUNTER')
        t = []
        for tuple in results['counter'].most_common(counter_max):
            t.append([tuple[1], _prepare_for_print(tuple[0])])
        _print_table(t)
    if print_resultset_stats:
        log('\nRESULTSET STATISTICS')
        t = []
        for key, value in results['resultset_stats'].items():
            t.append([key, value])
        _print_table(t)
    if print_counter_stats:
        log('\nCOUNTER STATISTICS')
        t = []
        for key, value in results['counter_stats'].items():
            t.append([key, value])

        _print_table(t)


def _print_table(table, headers=None, tabs=0):
    from tabulate import tabulate
    def_tablefmt = 'psql'
    tabs = ''.join(['\t' for num in range(tabs)])
    print()
    if headers:
        log(tabulate(table, floatfmt='.2f',
                     headers=headers, tablefmt=def_tablefmt))
    else:
        log(tabulate(table, floatfmt='.2f', tablefmt=def_tablefmt))


def _prepare_for_print(string):
    if string is None or len(str(string)) == 0:
        return '-'
    if not isinstance(string, str):
        return string
    from re import sub
    return sub('[\'"]+$', '', sub('^[\'"]+', '', string))

#############################################################################
# I/O SUPPORT
#############################################################################


def get_resource_filepath(basename):
    """Resolve the given basename to a resource filepath."""
    from os import path
    script_path = path.dirname(path.abspath(__file__))
    res_path = path.join(script_path, 'resource', basename)
    if not path.isdir(res_path) and not path.isfile(res_path):
        log('Resource file \'{}\' not found.'.format(res_path))
    return res_path


def read_valid_inputfiles(input_dir):
    """Read input file path from a folder determined by system-wide filter."""
    from robota.r_const import GLOBAL_INFILE_SUFFIX
    from bptbx import b_iotools
    file_list = b_iotools.findfiles(
        input_dir, '.*\.{}'.format(GLOBAL_INFILE_SUFFIX))
    return file_list


def get_key_from_url(url):
    """Generate a filesafe permakey from a given input url."""
    from re import sub
    from hashlib import md5
    file_key = sub('[^a-zA-Z0-9_-]', '_', url)
    file_key = sub('^http[s]?_', '', file_key)
    file_key = sub('^_+', '', file_key)
    file_key = sub('_+$', '', file_key)
    file_key = sub('^w+_+', '', file_key)[:80]
    chksum = md5(url.encode('utf-8')).hexdigest()
    file_key = file_key + '_' + chksum
    dir_key = file_key[:16]
    return file_key, dir_key

#############################################################################
# COMMAND-LINE LOGGING
#############################################################################


def _get_color(color='white'):
    from robota.r_const import COLOR_CODES
    try:
        return COLOR_CODES[color]
    except KeyError:
        return COLOR_CODES['white']


def log(message, color='yellow', err=False):
    """Write something to std-out distinguishable from regular output."""
    if not message or message is None:
        return
    color = _get_color(color)
    if err:
        import sys
        print('\x1b[{}m{}\x1b[0m'.format(
            color, message), file=sys.stderr)
    else:
        print('\x1b[{}m{}\x1b[0m'.format(color, message))


def logerr(message, color='red'):
    """Write something to std-err distinguishable from regular output."""
    log(message, color, err=True)


def notify_start(script):
    """Print out the title of a script on invocation."""
    if script is None or len(script) == 0:
        return
    from bptbx.b_iotools import basename
    from re import sub
    script = basename(script, '.py')
    script = sub('[_-]+', ' ', script).upper()
    log('\n +++ {} +++\n'.format(script), 'green', err=False)

#############################################################################
# PROGRESSBAR HANDLING
#############################################################################


def setup_progressbar(item_count):
    """Initialize a progressbar."""
    import progressbar
    from threading import Lock
    global p_bar, p_pointer, p_lock
    p_bar = progressbar.ProgressBar(max_value=item_count)
    p_pointer = 0
    p_lock = Lock()


def update_progressbar():
    """Update progressbar tick."""
    global p_bar, p_pointer, p_lock
    with p_lock:
        if not p_bar:
            return
        p_pointer += 1
        p_bar.update(p_pointer)


def finish_progressbar():
    """Notify finalization of process for progressbar."""
    global p_bar, p_pointer, p_lock
    if p_bar:
        p_bar.finish()
    print()

#############################################################################
# JSON MANIPULATION
#############################################################################


def object_to_json(obj):
    """Convert an object to a JSON-string."""
    import json
    json_string = json.dumps(obj, default=_internal_to_json)
    return json_string


def _internal_to_json(python_object):
    import time
    if isinstance(python_object, time.struct_time):
        return {'__class__': 'time.asctime',
                '__value__': time.asctime(python_object)}
    raise TypeError(repr(python_object) + ' is not JSON serializable')


def json_to_object(json_string):
    """Convert JSON-string to object."""
    import json
    obj = json.loads(json_string)
    return obj
