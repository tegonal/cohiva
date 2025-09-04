from os.path import abspath, dirname

from django.apps import apps as django_apps


def load_tests(loader, tests, pattern):
    if django_apps.is_installed("report"):
        return loader.discover(start_dir=dirname(abspath(__file__)), pattern=pattern)
