#!/usr/bin/env python3
"""Foo."""

if __name__ == '__main__':
    from os import environ
    from sys import argv
    from django.core.management import execute_from_command_line
    environ.setdefault("DJANGO_SETTINGS_MODULE", 'django_wrapper.django')
    execute_from_command_line(argv)
