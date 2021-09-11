from typing import List, Union

from django.apps import apps as APPS
from django.apps.config import AppConfig
from django.conf import settings

from introspection.model import ModelRepresentation


class AppInspector:
    """
    Inspect an app
    """

    app_config: AppConfig
    models: List[ModelRepresentation] = []

    def __init__(self, name: str) -> None:
        """
        Create an instance from an app name
        """
        app_config: Union[AppConfig, None] = None
        for appname in settings.INSTALLED_APPS:
            if appname == name:
                app_config = APPS.get_app_config(appname)
                break
        if app_config is not None:
            self.app_config = app_config
            return
        raise ModuleNotFoundError(f"App {name} was not found in settings")

    @property
    def name(self) -> str:
        """
        Get the app name
        """
        return self.app_config.name

    def get_models(self) -> None:
        """
        Get the app models
        """
        models_type = self.app_config.get_models()
        for model in models_type:
            self.models.append(ModelRepresentation.from_model_type(model))

    """def _convert_appname(self, appname: str) -> str:
        ""
        Remove the dots from an app name
        ""
        name = appname
        if "." in appname:
            name = appname.split(".")[-1]
        return name"""
