#!/usr/bin/env python3
"""Foo."""

if __name__ == "__main__":
    from os import environ
    environ.setdefault("DJANGO_SETTINGS_MODULE", "django_wrapper.django")
    from django.core.management import execute_from_command_line
    execute_from_command_line(['./manage.py', 'runserver', 'localhost:1337'])
