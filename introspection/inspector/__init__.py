from __future__ import print_function
from django.db.models import Q
from django.conf import settings
from django.apps import apps as APPS
from django.utils.html import strip_tags
from django.contrib.contenttypes.fields import GenericForeignKey
from goerr import err, colors
from .users import UserInspector
TERM = "term" in settings.INSTALLED_APPS
if TERM:
    from term.commands import rprint as RPRINT


class Inspector(UserInspector):
    allowed_apps = []
    appnames = []

    def __init__(self):
        self.allowed_apps = self.apps()

    def scanapp(self, path=None, term=False):
        global TERM
        global RPRINT
        rprint = prints
        if term is True:
            if TERM is True:
                rprint = RPRINT
            else:
                err.new(self.scanapp,
                        "Terminal is not installed: can not remote print")
                return
        if path is None:
            return "A path is required: ex: auth.User"
        has_model = "." in path
        if has_model is False:
            appname = path
            stats = self.app(appname)
            for modelname in stats:
                if TERM is False:
                    msg = colors.bold(str(stats[modelname]))
                else:
                    msg = "<b>" + str(stats[modelname]) + "</b>"
                rprint("<b>" + modelname + "</b>", ": found",
                       msg + " instances")
            return
        else:
            path = path
            s = path.split(".")
            appname = s[0]
            modelname = s[1]
            infos = self.model(appname, modelname)
            title("Fields")
            if TERM is False:
                rprint("# Found", colors.bold(
                    str(len(infos["fields"])) + " fields:"))
            else:
                rprint("# Found<b>", str(
                    len(infos["fields"])) + "</b> fields:")
            for field in infos["fields"]:
                if TERM is True:
                    name = "<b>" + field["name"] + "</b>"
                else:
                    name = colors.green(field["name"])
                ftype = field["class"]
                rel = field["related"]
                msg = name + " " + ftype
                if rel is not None:
                    msg = msg + " with related name " + rel
                rprint(msg)
            numrels = len(infos["relations"])
            if numrels > 0:
                relstr = "relations"
                if numrels == 1:
                    relstr = "relation"
                title("Relations")
                if TERM is False:
                    rprint("# Found", colors.bold(str(len(infos["relations"])) +
                                                  " external " + relstr), ":")
                else:
                    rprint("# Found<b>",
                           str(infos["count"]) + "</b> instances of " + modelname)
                for rel in infos["relations"]:
                    if TERM is True:
                        name = "<b>" + rel["field"] + "</b>"
                    else:
                        name = colors.green(rel["field"])
                    relname = rel["related_name"]
                    relfield = rel["relfield"]
                    relstr = ""
                    if relname is not None:
                        relstr = "with related name " + colors.green(relname)
                    rprint(name, "from", relfield, rel["type"], relstr)
            title("Instances")
            if TERM is False:
                rprint("# Found", colors.bold(
                    str(infos["count"]) + " instances of " + modelname))
            else:
                rprint("# Found <b>" + str(numrels) + "</b> relations")

    def apps(self):
        apps = []
        self.appnames = []
        for appname in settings.INSTALLED_APPS:
            appname = self._convert_appname(appname)
            self.appnames.append(appname)
            app = APPS.get_app_config(appname)
            apps.append(app)
        if err.exists:
            err.report()
            return
        return apps

    def app_names(self):
        apps = []
        self.appnames = []
        for appname in settings.INSTALLED_APPS:
            appname = self._convert_appname(appname)
            self.appnames.append(appname)
            apps.append(self._convert_appname(appname))
        if err.exists:
            err.report()
            return
        return apps

    def app(self, appname):
        appstats = {}
        models = self._models(appname)
        if err.exists:
            err.new("Can not get models for app " + appname, self.app)
            return appstats
        for model in models:
            count = self._count_model(model)
            if err.exists:
                err.new("Can not count model", self.app)
                return appstats
            appstats[model.__name__] = count
        if err.exists:
            err.report()
            return
        return appstats

    def model(self, appname, modelname):
        model = self._get_model(appname, modelname)
        if err.exists:
            return
        count = self._count_model(model)
        if err.exists:
            return
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
                relfield = field.get_related_field()
                rel = {"field": str(field.field), "relfield": str(
                    relfield), "related_name": field.related_name, "type": cl}
                relations.append(rel)
            else:
                fobj = {"name": field.name, "class": ftype, "related": None}
                relfields = ["OneToOneField", "ForeignKey", "ManyToManyField"]
                if ftype in relfields:
                    relstr = str(field.remote_field.name)
                    fobj["related"] = relstr
                fields.append(fobj)
        info["fields"] = fields
        info["relations"] = relations
        if err.exists:
            err.report()
            return
        return info

    def models(self, appname):
        models = self._models(appname)
        if err.exists:
            err.report()
            return
        return models

    def has_m2m(self, model):
        ftypes = model._meta.get_fields(include_parents=False)
        for field in ftypes:
            if isinstance(field, GenericForeignKey):
                continue
            if field.get_internal_type() == "ManyToManyField":
                return True
        return False

    def field_type(self, model, fieldname):
        ftypes = model._meta.get_fields(include_parents=False)
        ftype = None
        for field in ftypes:
            if field.name == fieldname:
                ftype = field.get_internal_type()
        return ftype

    def count(self, jsonq, operator="and"):
        q = self.query(jsonq, operator, count=True)
        if err.exists:
            err.report()
            return
        return q

    def query(self, jsonq, operator="and", count=False):
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
            q = model.objects.none()
        except Exception as e:
            err.new(e)
        for label in fdict:
            kwargs = {label: fdict[label]}
            filters.append(Q(**kwargs))
        if filters == []:
            try:
                q = model.objects.all()
                return q, err
            except Exception as e:
                err.new(e)
        else:
            fq = Q()
            for f in filters:
                if operator == "and":
                    fq = fq & f
                elif operator == "or":
                    fq = fq | f
            if count is False:
                try:
                    q = model.objects.filter(fq)
                except Exception as e:
                    err.new(e)
            else:
                try:
                    q = model.objects.filter(fq).count()
                except Exception as e:
                    err.new(e)
        if err.exists:
            err.report()
        return q

    def _models(self, appname):
        """
        return models_array
        """
        app = self._get_app(appname)
        if err.exists:
            err.new("Can not get app " + appname, self.models)
            return
        if appname not in self.appnames:
            err.new("App " + appname + " not found in settings")
            return
        models = self._get_models(app)
        if err.exists:
            return
        return models

    def _get_app(self, appname):
        """
        returns app object or None
        """
        try:
            app = APPS.get_app_config(appname)
        except Exception as e:
            err.new(e)
            return
        return app

    def _get_model(self, appname, modelname):
        """
        return model or None
        """
        app = self._get_app(appname)
        if err.exists:
            err.new("Can not get model " + modelname +
                    " from app " + app, self._get_model)
        models = app.get_models()
        model = None
        for mod in models:
            if mod.__name__ == modelname:
                model = mod
                return model
        msg = "Model " + modelname + " not found"
        err.new(msg)

    def _get_models(self, app):
        """
        return models_array
        """
        try:
            app_models = app.get_models()
            appmods = []
            for model in app_models:
                appmods.append(model)
        except Exception as e:
            err.new(e)
            return
        return appmods

    def _count_model(self, model):
        """
        return model count
        """
        try:
            res = model.objects.all().count()
        except Exception as e:
            err.new(e)
            return
        return res

    def _convert_appname(self, appname):
        name = appname
        if "." in appname:
            name = appname.split(".")[-1]
        return name


inspect = Inspector()


def title(name):
    print("========================================================")
    print("                     " + name)
    print("========================================================")


def prints(*args):
    msg = ""
    for arg in args:
        msg += strip_tags(arg) + " "
    print(msg)
