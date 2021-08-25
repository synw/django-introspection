from django.core.management.base import BaseCommand

from introspection.inspector import inspect


class Command(BaseCommand):
    help = "Inspect an application or model"

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        path = options["path"]
        inspect.scanapp(path)
        return
