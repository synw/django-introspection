# pylint: disable=no-member
from typing import Iterator, List, Type, Union

from django.apps import apps as APPS
from django.apps.config import AppConfig
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Model, Q
from django.db.models.query import QuerySet

from ..colors import colors
from .users import UserInspector


class Inspector(UserInspector):
    allowed_apps = []
    appnames = []

    def __init__(self):
        self.allowed_apps = self.apps()

    def scanapp(self, path: Union[str, None] = None) -> None:
        if path is None:
            raise AttributeError("A path is required: ex: auth.User")
        has_model = "." in path
        if has_model is False:
            appname = path
            stats = self.app(appname)
            for modelname in stats:
                msg = colors.bold(str(stats[modelname]))
                print(modelname, ": found", msg + " instances")
            return
        else:
            path = path
            s = path.split(".")
            appname = s[0]
            modelname = s[1]
            infos = self.model(appname, modelname)
            title("Fields")
            print("# Found", colors.bold(str(len(infos["fields"])) + " fields:"))
            for field in infos["fields"]:
                name = colors.green(field["name"])
                ftype = field["class"]
                rel = field["related"]
                msg = name + " " + ftype
                if rel is not None:
                    msg = msg + " with related name " + rel
                print(msg)
            numrels = len(infos["relations"])
            if numrels > 0:
                relstr = "relations"
                if numrels == 1:
                    relstr = "relation"
                title("Relations")
                print(
                    "# Found",
                    colors.bold(str(len(infos["relations"])) + " external " + relstr),
                    ":",
                )
                for rel in infos["relations"]:
                    name = colors.green(rel["field"])
                    relname = rel["related_name"]
                    relfield = rel["relfield"]
                    relstr = ""
                    if relname is not None:
                        relstr = "with related name " + colors.green(relname)
                    print(name, "from", relfield, rel["type"], relstr)
            title("Instances")
            print(
                "# Found",
                colors.bold(str(infos["count"]) + " instances of " + modelname),
            )

    def apps(self) -> List[AppConfig]:
        apps: List[AppConfig] = []
        self.appnames = []
        for appname in settings.INSTALLED_APPS:
            appname = self._convert_appname(appname)
            self.appnames.append(appname)
            app = APPS.get_app_config(appname)
            apps.append(app)
        return apps

    def app_names(self) -> List[str]:
        apps: List[str] = []
        self.appnames = []
        for appname in settings.INSTALLED_APPS:
            appname = self._convert_appname(appname)
            self.appnames.append(appname)
            apps.append(self._convert_appname(appname))
        return apps

    def app(self, appname: str) -> dict:
        appstats = {}
        try:
            models = self._models(appname)
        except Exception as e:
            raise Exception("Can not get models for app " + appname, self.app, e)
        for model in models:
            try:
                count = self._count_model(model)
            except Exception as e:
                raise Exception("Can not count model", e)
            appstats[model.__name__] = count
        return appstats

    def model(self, appname: str, modelname: str):
        model = self._get_model(appname, modelname)
        if model is None:
            raise Exception(f"Model {modelname} not found")
        count = self._count_model(model)
        info = {}
        info["count"] = count
        f = model._meta.get_fields(include_parents=False)
        fields = []
        relations = []
        for field in f:
            ftype = field.get_internal_type()
            cl = field.__class__.__name__
            rels = ["OneToOneField", "ManyToOneRel", "ManyToManyRel"]
            if cl in rels:
                try:
                    relfield = field.get_related_field()  # type: ignore
                    rel = {
                        "field": str(field.field),  # type: ignore
                        "relfield": str(relfield),
                        "related_name": field.related_name,  # type: ignore
                        "type": cl,
                    }
                    relations.append(rel)
                except Exception as e:
                    raise e
            else:
                fobj = {"name": field.name, "class": ftype, "related": None}
                relfields = ["OneToOneField", "ForeignKey", "ManyToManyField"]
                if ftype in relfields:
                    relstr = str(field.remote_field.name)
                    fobj["related"] = relstr
                    fobj[
                        "related_class"
                    ] = field.related_model().__class__.__name__  # type: ignore
                fields.append(fobj)
        info["fields"] = fields
        info["relations"] = relations
        return info

    def models(self, appname: str) -> Iterator[Type[Model]]:
        try:
            models = self._models(appname)
        except Exception as e:
            raise Exception("Can not get models", e)
        return models

    def has_m2m(self, model: Type[Model]) -> bool:
        ftypes = model._meta.get_fields(include_parents=False)
        for field in ftypes:
            if isinstance(field, GenericForeignKey):
                continue
            if field.get_internal_type() == "ManyToManyField":
                return True
        return False

    def field_type(self, model: Type[Model], fieldname: str) -> Union[str, None]:
        ftypes = model._meta.get_fields(include_parents=False)
        ftype = None
        for field in ftypes:
            if field.name == fieldname:
                ftype = field.get_internal_type()
        return ftype

    # def count(self, jsonq, operator="and") -> int:
    #    q = self.query(jsonq, operator, count=True)
    #    return int(q)

    def query(
        self, jsonq: dict, operator: str = "and", count: bool = False
    ) -> QuerySet:
        """
        returns a Django orm query from json input:
        {
        "app": "auth",
        "model": "User",
        "filters": {
            "is_superuser": False,
            "username__icontains": "foo"
        }
        """
        model = self._get_model(jsonq["app"], jsonq["model"])
        fdict = jsonq["filters"]
        filters = []
        try:
            q = model.objects.none()  # type: ignore
        except Exception as e:
            raise e
        for label in fdict:
            kwargs = {label: fdict[label]}
            filters.append(Q(**kwargs))
        q: QuerySet
        if filters == []:
            try:
                q = model.objects.all()  # type: ignore
                return q
            except Exception as e:
                raise e
        else:
            fq = Q()
            for f in filters:
                if operator == "and":
                    fq = fq & f
                elif operator == "or":
                    fq = fq | f
            if count is False:
                try:
                    q = model.objects.filter(fq)  # type: ignore
                except Exception as e:
                    raise e
            else:
                try:
                    q = model.objects.filter(fq).count()  # type: ignore
                except Exception as e:
                    raise e
        return q  # pyright: reportUnboundVariable=false

    def _models(self, appname) -> Iterator[Type[Model]]:
        """
        return models_array
        """
        try:
            app = self._get_app(appname)
        except Exception as e:
            raise Exception(f"Can not get app {appname} {e}")
        if appname not in self.appnames:
            raise Exception("App " + appname + " not found in settings")
        models = app.get_models()
        return models

    def _get_app(self, appname) -> AppConfig:
        """
        returns app object or None
        """
        try:
            app = APPS.get_app_config(appname)
        except Exception as e:
            raise e
        return app

    def _get_model(self, appname, modelname) -> Union[Type[Model], None]:
        """
        return model or None
        """
        app = self._get_app(appname)
        models = app.get_models()
        model = None
        for mod in models:
            if mod.__name__ == modelname:
                model = mod
                return model
        # msg = "Model " + modelname + " not found"

    def _count_model(self, model) -> int:
        """
        return model count
        """
        try:
            res = model.objects.all().count()
        except Exception as e:
            raise e
        return res

    def _convert_appname(self, appname: str) -> str:
        name = appname
        if "." in appname:
            name = appname.split(".")[-1]
        return name


inspect = Inspector()


def title(name):
    print("========================================================")
    print("                     " + name)
    print("========================================================")
