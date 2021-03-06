"""Processing utilities."""


def process_input_file_with_optional_collection(
        args, col, db_file_field, worker_method, threads=None, query={}):
    """Process all files from the given folder optionally using mongo data."""
    from bptbx import b_threading
    from robota import r_util, r_mongo
    from os import path

    threads = args.t if not threads else threads
    r_util.log('Using {} thread(s) for processing...'.format(threads))

    pool = b_threading.ThreadPool(threads)
    if args.i and not col:
        in_files = r_util.read_valid_inputfiles(args.i)
        r_util.setup_progressbar(len(in_files))
        for in_file in in_files:
            pool.add_task(worker_method, in_file)
    else:
        cursor = r_mongo.find_docs(col, query, no_cursor_timeout=True)
        r_util.setup_progressbar(cursor.count())
        for doc in cursor:
            field = r_mongo.get_key_nullsafe(doc, db_file_field)
            if field:
                in_file = path.join(args.i, field)
                pool.add_task(worker_method, in_file, col, doc)
        cursor.close()
    pool.wait_completion()
    r_util.finish_progressbar()

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
    print_table(t)

    if print_counter:
        log('\nCOUNTER')
        t = []
        total = float(sum(results['counter'].values()))
        for tuple in results['counter'].most_common(counter_max):
            ratio = float(tuple[1]) / total * 100
            t.append([tuple[1], ratio, _prepare_for_print(tuple[0])])
        print_table(t)
    if print_resultset_stats:
        log('\nRESULTSET STATISTICS')
        t = []
        for key, value in results['resultset_stats'].items():
            t.append([key, value])
        print_table(t)
    if print_counter_stats:
        log('\nCOUNTER STATISTICS')
        t = []
        for key, value in results['counter_stats'].items():
            t.append([key, value])

        print_table(t)


def print_table(table, headers=None, colors=True):
    """Print the given list of lists using tabulate."""
    from tabulate import tabulate
    def_tablefmt = 'psql'
    print_method = log if colors else print
    lines = get_table_string(table, headers)
    for line in lines:
        print_method(line)


def get_table_string(table, headers=None, colors=True):
    """Creates a table string for the given list of lists using tabulate."""
    from tabulate import tabulate
    def_tablefmt = 'psql'
    lines = []
    if headers:
        lines.append(tabulate(table, floatfmt='.2f',
                              headers=headers, tablefmt=def_tablefmt))
    else:
        lines.append(tabulate(table, floatfmt='.2f', tablefmt=def_tablefmt))
    return lines


def _prepare_for_print(string):
    if string is None or len(str(string)) == 0:
        return '-'
    if not isinstance(string, str):
        return string
    from re import sub
    return sub('[\'"]+$', '', sub('^[\'"]+', '', string))


def print_map(input_map, value_length_limit=0):
    """Print a map to console table-formatted."""
    table = []
    for key in sorted(input_map.keys()):
        value = '{}'.format(input_map[key])
        value_type = type(value).__name__
        if value_length_limit > 0:
            value = value[:value_length_limit]
        table.append([key, value, value_type])
    print_table(table, ['Key', 'Value', 'Type'])

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


def setup_progressbar(item_count, verbose=True):
    """Initialize a progressbar."""
    import progressbar
    from threading import Lock
    global p_bar, p_pointer, p_lock, p_verbose
    p_verbose = verbose
    if not p_verbose:
        return
    p_bar = progressbar.ProgressBar(max_value=item_count)
    p_pointer = 0
    p_lock = Lock()


def update_progressbar():
    """Update progressbar tick."""
    global p_bar, p_pointer, p_lock, p_verbose
    if not p_verbose:
        return
    with p_lock:
        if not p_bar:
            return
        p_pointer += 1
        p_bar.update(p_pointer)


def finish_progressbar():
    """Notify finalization of process for progressbar."""
    global p_bar, p_pointer, p_lock, p_verbose
    if not p_verbose:
        return
    if p_bar:
        p_bar.finish()
    print()

#############################################################################
# JSON MANIPULATION
#############################################################################


def object_to_file(obj, file, indent=4, explicit_class=True):
    """Write an object to the given file handle."""
    import json
    def_method = _to_json_explicit if explicit_class else _to_json_value
    json.dump(obj, file, indent=indent, default=def_method)


def object_to_json(obj, explicit_class=True):
    """Convert an object to a JSON-string."""
    import json
    def_method = _to_json_explicit if explicit_class else _to_json_value
    json_string = json.dumps(obj, default=def_method)
    return json_string


def json_to_object(json_string):
    """Convert JSON-string to object."""
    import json
    obj = json.loads(json_string)
    return obj


def _to_json_value(python_object):
    return _to_json_impl(python_object, False)


def _to_json_explicit(python_object):
    return _to_json_impl(python_object, True)


def _to_json_impl(python_object, explicit):
    import time
    import datetime
    if isinstance(python_object, time.struct_time):
        value = time.asctime(python_object)
        if explicit:
            return {'__class__': 'time.asctime',
                    '__value__': value}
        else:
            return value
    if isinstance(python_object, datetime.datetime):
        value = python_object.isoformat()
        if explicit:
            return {'__class__': 'time.asctime',
                    '__value__': value}
        else:
            return value
    raise TypeError(repr(python_object) + ' is not JSON serializable')
