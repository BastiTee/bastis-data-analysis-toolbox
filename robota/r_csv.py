"""Utilities to work with CSV-separated files."""


def _filter_applies(row, filters):
    for f in filters:
        if not f[1](row.get(f[0], None)):
            return True
    return False


def _apply_search_replace(row, searchreplace):
    from re import sub
    if len(searchreplace) == 0:
        return row
    for triplet in searchreplace:
        row[triplet[2]] = sub(triplet[0], triplet[1], row[triplet[2]])
    return row


def generate_csv_object(file, header, delimiter=';', quotechar='\"',
                        encoding='iso-8859-1', filters=[], searchreplace=[]):
    """Generate a map from a CSV file and count columns.

    - Example for a filter:
        filters=[
            ('position', lambda x: int(x) == 1),
        ])
    """
    from csv import reader, DictReader
    from collections import Counter

    if not header:
        # generate dummy fieldnames if no header is present
        csv_in = reader(open(file, 'r', encoding=encoding),
                        delimiter=delimiter, quotechar=quotechar)
        lens = max([len(row) for row in csv_in])
        fieldnames = list(range(lens))
    else:
        fieldnames = None

    csv_in = DictReader(
        open(file, 'r', encoding=encoding), delimiter=delimiter,
        quotechar=quotechar, fieldnames=fieldnames)

    # create a list of maps for the input csv
    res_list = []
    for row in csv_in:
        # ... but apply filters
        if _filter_applies(row, filters):
            continue
        else:
            _apply_search_replace(row, searchreplace)
            res_list.append(row)

    # keep the fieldnames
    res_fields = csv_in.fieldnames

    # count the fields for a quick overview
    res_counter = {}
    for fieldname in res_fields:
        values = [res[fieldname] for res in res_list
                  if res.get(fieldname, None) is not None]
        counter = Counter(values)
        res_counter[fieldname] = counter

    return {
        'rows': res_list,
        'fieldnames': res_fields,
        'fieldcounter': res_counter,
    }


def pretty_print_csv_obj(csv_obj, max_vals=10, colors=False):
    """Print a CSV object to console."""
    from robota.r_util import print_table
    for field in csv_obj['fieldnames']:
        print('=== {}\n'.format(field.upper()))
        c = csv_obj['fieldcounter'][field]
        print('ORG-FIELDNAME: \'{}\''.format(field))
        print('TOTAL-COUNT:   {}'.format(sum(c.values())))
        print('UNIQUE-KEYS:   {}'.format(len(c.keys())))
        print('TOP {} VALUES:'.format(max_vals))
        print_table(c.most_common(max_vals), colors=colors)
        print()


def pretty_write_csv_obj(csv_obj, file_o, max_vals=10):
    """Print a CSV object to file."""
    from robota.r_util import get_table_string
    f_handle = open(file_o, 'w')
    for field in csv_obj['fieldnames']:
        f_handle.write('=== {}\n\n'.format(field.upper()))
        c = csv_obj['fieldcounter'][field]
        f_handle.write('ORG-FIELDNAME: \'{}\'\n'.format(field))
        f_handle.write('TOTAL-COUNT:   {}\n'.format(sum(c.values())))
        f_handle.write('UNIQUE-KEYS:   {}\n'.format(len(c.keys())))
        f_handle.write('TOP {} VALUES:\n'.format(max_vals))
        table = get_table_string(
            c.most_common(max_vals), colors=False)
        for line in table:
            f_handle.write(line)
        f_handle.write('\n\n')


def write_csv_object(csv_obj, file, delimiter=';',
                     quotechar='\"', encoding='iso-8859-1', header=True):
    """Write a CSV object to the given file."""
    from csv import writer, QUOTE_MINIMAL
    header = csv_obj['fieldnames']
    file_handle = open(file, 'w', encoding=encoding)
    csv_writer = writer(file_handle, delimiter=delimiter,
                        quotechar=quotechar, quoting=QUOTE_MINIMAL)
    csv_writer.writerow(header)
    for row in csv_obj['rows']:
        flat_row = [row[fieldname] for fieldname in csv_obj['fieldnames']]
        csv_writer.writerow(flat_row)


def write_array_of_arrays(arrarray, file, delimiter=';',
                          quotechar='\"', encoding='iso-8859-1', header=True):
    """Write an array of arrays to the given file."""
    from csv import writer, QUOTE_MINIMAL
    file_handle = open(file, 'w', encoding=encoding)
    csv_writer = writer(file_handle, delimiter=delimiter,
                        quotechar=quotechar, quoting=QUOTE_MINIMAL)
    for row in arrarray:
        csv_writer.writerow(row)
