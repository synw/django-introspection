from typing import List
from introspection.model import ModelRepresentation
from django.core.management.base import BaseCommand

# from introspection.inspector import inspect
from introspection.inspector.inspector import AppInspector
from introspection.inspector import title, subtitle
from introspection.colors import colors


class Command(BaseCommand):
    help = "Inspect an application or model"

    def inspect_model_fields(self, model: ModelRepresentation) -> None:
        """
        Print model fields info
        """
        c = model.count()
        title(f"{model.name} ({c})")
        print(model.fields_info())

    def inspect_model_relations(self, model: ModelRepresentation) -> None:
        """
        Print model relations info
        """
        subtitle("Relations")
        for field in model.fields.values():
            if field.is_relation is True:
                try:
                    relfield = field._raw_field.remote_field.name  # type: ignore
                    raw = field._raw_field.related_model()  # type: ignore
                    msg = colors.yellow(field.name)
                    msg += " -> " + str(raw.__class__.__module__)
                    msg += "." + str(raw.__class__.__qualname__)
                    msg += f".{relfield}"
                    print(msg)
                except Exception:
                    print(
                        f"No related field for {field} of type {type(field._raw_field)}"
                    )

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        path = options["path"]
        if path is None:
            raise AttributeError("A path is required: ex: auth.User")
        appname = path
        modelname = None
        if "." in path:
            p = path.split(".")
            appname = p[0]
            modelname = p[-1]
        app = AppInspector(appname)
        model_names: List[ModelRepresentation] = []
        if modelname is not None:
            model_names = [ModelRepresentation(app_name=appname, model_name=modelname)]
        else:
            app.get_models()
            model_names = app.models
        if modelname is None:
            print(f"App {app.name} models:")
        else:
            print(f"Model {model_names[0]}")
        for model in model_names:
            self.inspect_model_fields(model)
            self.inspect_model_relations(model)
