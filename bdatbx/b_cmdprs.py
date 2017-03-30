r"""Command-line parsing presets."""


from bptbx.b_iotools import file_exists
from argparse import ArgumentParser
from os import path, getcwd, chdir
from bdatbx import b_util


def init(info=''):
    return ArgumentParser(description=info)


def show_help(prs, message):
    print(message)
    prs.print_help()
    exit(1)


# FILE IN ---------------------------------------------------------------------


def add_file_in(prs):
    prs.add_argument('-i', metavar='INPUT', help='Input file')


def check_file_in(prs, args):
    if not args.i:
        show_help(prs, 'No input file set.')
    if not file_exists(args.i):
        show_help(prs, 'Input file does not exist.')
    args.i = path.abspath(args.i)


# DIRECTORY IN ----------------------------------------------------------------


def add_dir_in(prs, label='Input directory'):
    prs.add_argument('-i', metavar='INPUT', help=label)


def check_dir_in(prs, args):
    if not args.i:
        show_help(prs, 'No input directory set.')
    if not path.isdir(args.i):
        show_help(prs, 'Input directory does not exist.')
    args.i = path.abspath(args.i)


# FILE OUT --------------------------------------------------------------------


def add_file_out(prs):
    prs.add_argument('-o', metavar='OUTPUT', help='Output file')


def check_file_out(prs, args):
    if args.o is None:
        show_help(prs, 'No output file provided.')
    if file_exists(args.o):
        show_help(prs, 'Output file already exists.')
    args.o = path.abspath(args.o)


# DIRECTORY OUT ---------------------------------------------------------------


def add_dir_out(prs):
    prs.add_argument('-o', metavar='OUTPUT', help='Output directory')


def check_dir_out_and_chdir(prs, args):
    if not args.o:
        show_help(prs, 'No output directory set.')
    if not path.isdir(args.o):
        show_help(prs, 'Output directory does not exist.')
    args.o = path.abspath(args.o)
    chdir(args.o)
    b_util.log('STARTED {}'.format(b_util.get_calling_module(1)), 1, '0;32',
               prefix=True)
    b_util.log('Working directory {}'.format(getcwd()), 1, prefix=True)


# AUXILIARY- ------------------------------------------------------------------


def add_opt_dir_in(prs, opt, label):
    prs.add_argument(opt, metavar='IN_DIR', help=label)


def check_opt_dir_in(prs, arg, info='Optional directory does not exist.'):
    if arg is None:
        return
    if not path.isdir(arg):
        show_help(prs, info)
    return path.abspath(arg)


def add_opt_file_in(prs, opt, label):
    prs.add_argument(opt, metavar='IN_FILE', help=label)


def check_opt_file_in(prs, arg, info='Optional file does not exist.'):
    if arg is None:
        return
    if not path.isfile(arg):
        show_help(prs, info)
    return path.abspath(arg)


def add_verbose(prs):
    prs.add_argument('-v', action='store_true',
                     help='Verbose output', default=False)


def add_mongo_collection(prs):
    prs.add_argument('-c', default='', help='MongoDB collection name')


def check_mongo_collection(prs, args, required=False):
    if not args.c and required:
        show_help(prs, 'MongoDB collection required but not set.' )
    from bdatbx import b_mongo
    col = b_mongo.get_client_for_collection(args.c, create=False)
    if not col:
        show_help(prs, 'Given MongoDB collection does not exist.' )
    return col


def add_bool(prs, opt, label):
    prs.add_argument(opt, action='store_true', help=label, default=False)


def add_max_threads(prs):
    prs.add_argument('-t', metavar='THREADS',
                     help='Number of threads', default=10)


def check_max_threads(prs, args):
    try:
        args.t = int(args.t)
    except ValueError:
        show_help(prs, 'Invalid number of threads.')
    if int(args.t) <= 0:
        show_help(prs, 'Invalid number of threads.')
