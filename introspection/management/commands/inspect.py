from __future__ import print_function
from django.core.management.base import BaseCommand
from introspection.inspector import inspect


class Command(BaseCommand):
    help = 'Inspect an application or model'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)

    def handle(self, *args, **options):
        path = options["path"]
        err = inspect.scanapp(path)
        if err != None:
            print("Error scanning app:", err)
        return
