# from __future__ import annotations
from typing import Dict, List, Optional, Type, Union

from django.apps import apps as APPS
from django.apps.config import AppConfig
from django.db.models import Model
from django.db.models.fields import Field
from django.db.models.fields.reverse_related import ForeignObjectRel

from introspection.colors import colors
from .const import RELATIONS, RELATIONS_FIELDS


class ModelFieldRepresentation:
    """
    Representation of a Django model field
    """

    name: str
    classname: str
    related_name: str = ""
    related_class_name: str = ""
    _raw_field: Union[Field, ForeignObjectRel]

    def __init__(self, field: Union[Field, ForeignObjectRel]) -> None:
        """
        Initialize from a Django field
        """
        self.name = field.name
        self._raw_field = field
        self.classname = field.get_internal_type()
        self._get_related_name()

    def __repr__(self) -> str:
        s = f"<{self.name}: {self.classname}"
        if self.is_relation is True:
            s += f" - relation: {self.related_class_name} ({self.related_name})"
        return s + ">"

    @property
    def is_relation(self) -> bool:
        """
        Check if the field is a relation
        """
        return self.related_class_name != ""

    @property
    def is_blank(self) -> bool:
        """
        Check if a field is blank
        """
        return self._raw_field.blank  # type: ignore

    @property
    def is_null(self) -> bool:
        """
        Check if a field is null
        """
        return self._raw_field.null

    def to_dict(self) -> Dict[str, str]:
        """
        Dict representation of a field
        """
        return {
            "name": self.name,
            "class": self.classname,
            "related_name": self.related_class_name,
        }

    @property
    def info(self) -> str:
        """
        Get the field's info
        """
        name = colors.green(self.name)
        ftype = self.classname
        msg = name + " " + ftype
        if self.is_blank is True:
            msg += " blank"
        if self.is_null is True:
            msg += " null"
        if self.is_relation is True:
            msg = msg + " with related name " + self.related_class_name
        return msg

    def _get_related_name(self) -> None:
        if self.classname in RELATIONS_FIELDS:
            self.related_name = str(self._raw_field.remote_field.name)
            self.related_class_name = (
                self._raw_field.related_model().__class__.__name__  # type: ignore
            )


class ModelRepresentation:
    """
    Representation of a Django model
    """

    name: str
    fields: Dict[str, ModelFieldRepresentation] = {}
    fks: Dict[str, ModelFieldRepresentation] = {}
    _model_type: Type[Model]

    def __init__(
        self,
        app_name: Optional[str] = None,
        model_name: Optional[str] = None,
        model_type: Optional[Type[Model]] = None,
    ) -> None:
        """
        Initialize a model representation
        """
        if model_type:
            self._model_type = model_type
        elif app_name and model_name:
            self._model_type = self._get(app_name, model_name)
        else:
            raise ValueError(
                "Please provide either a model_type or and app_name and model_name"
            )
        self._get_fields()
        self.name = self._model_type.__name__

    def __repr__(self) -> str:
        return "<" + self.name + ">"

    @staticmethod
    def from_model_type(model_type: Type[Model]) -> "ModelRepresentation":
        """
        Create a model representation from a Model type
        """
        return ModelRepresentation(model_type=model_type)

    def count(self) -> int:
        """
        Return a models instances count
        """
        return self._model_type.objects.all().count()

    def fields_info_buffer(self) -> List[str]:
        """
        Get the model's fields infos's string buffer
        """
        buf: List[str] = [f"# {len(self.fields)} fields"]
        for field in self.fields.values():
            buf.append(field.info)
        return buf

    def fields_info(self) -> str:
        """
        Print the model's fields infos string
        """
        return "\n".join(self.fields_info_buffer())

    def _get(self, app_name: str, model_name: str) -> Type[Model]:
        """
        return model type or None
        """
        app: AppConfig
        try:
            app = APPS.get_app_config(app_name)
        except LookupError as e:
            raise e
        models = app.get_models()
        model = None
        for mod in models:
            if mod.__name__ == model_name:
                model = mod
        if model is None:
            raise LookupError(f"Model {model_name} not found for app {app_name}")
        return model

    def _get_fields(self) -> None:
        """
        Set the model fields list representation
        """
        fs: List[Union[Field, ForeignObjectRel]] = self._model_type._meta.get_fields(
            include_parents=False
        )
        self.fields = {}
        for field in fs:
            cl = field.__class__.__name__
            if cl not in RELATIONS:
                f = ModelFieldRepresentation(field)
                self.fields[f.name] = f
