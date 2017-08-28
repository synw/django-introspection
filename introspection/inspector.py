from __future__ import print_function
from django.db.models import Q
from django.conf import settings
from django.apps import apps as APPS
from django.utils.html import strip_tags
from blessings import Terminal
from goerr import err
TERM = "terminal" in settings.INSTALLED_APPS
if TERM:
    from terminal.commands import rprint as RPRINT


class Inspector:
    allowed_apps = []
    appnames = []
    p = Terminal()

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
                return "Terminal is not installed: can not remote print"
        if path == None:
            return "A path is required: ex: auth.User"
        has_model = "." in path
        if has_model is False:
            appname = path
            stats, error = self.app(appname)
            if error is not None:
                return error
            for modelname in stats:
                rprint("<b>" + modelname + "</b>", ": found",
                       self.p.bold(stats[modelname] + " instances"))
            return None
        else:
            path = path
            s = path.split(".")
            appname = s[0]
            modelname = s[1]
            infos, error = self.model(appname, modelname)
            if error is not None:
                return error
            title("Fields")
            rprint("# Found", self.p.bold(
                str(len(infos["fields"])) + " fields:"))
            for field in infos["fields"]:
                if TERM is True:
                    name = "<b>" + field["name"] + "</b>"
                else:
                    name = self.p.bold_green(field["name"])
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
                rprint("# Found", self.p.bold(str(len(infos["relations"])) +
                                              " external " + relstr), ":")
                for rel in infos["relations"]:
                    if TERM is True:
                        name = "<b>" + rel["field"] + "</b>"
                    else:
                        name = self.p.bold_green(rel["field"])
                    relname = rel["related_name"]
                    relfield = rel["relfield"]
                    relstr = ""
                    if relname is not None:
                        relstr = "with related name " + self.p.green(relname)
                    rprint(name, "from", relfield, rel["type"], relstr)
            title("Instances")
            rprint("# Found", self.p.bold(
                str(infos["count"]) + " instances of " + modelname))
        return None

    def apps(self):
        apps = []
        for appname in settings.INSTALLED_APPS:
            appname = self._convert_appname(appname)
            self.appnames.append(appname)
            app = APPS.get_app_config(appname)
            apps.append(app)
        return apps

    def app(self, appname):
        appstats = {}
        models, error = self.models(appname)
        if error is not None:
            return None, error
        for model in models:
            count, error = self._count_model(model)
            if error is not None:
                return None, error
            appstats[model.__name__] = count
        return appstats, None
    """
    def count(self, appname, modelname):
        model = self._get_model(appname, modelname)
        res = model.objects.all().count()
        return res
    """

    def model(self, appname, modelname):
        model, error = self._get_model(appname, modelname)
        if error is not None:
            return None, error
        count, error = self._count_model(model)
        if error is not None:
            return None, error
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
        return info, None

    def models(self, appname):
        """
        return models_array, error
        """
        app = self._get_app(appname)
        if appname not in self.appnames:
            return None, "App " + appname + " not found in settings"
        models, error = self._get_models(app)
        if error is not None:
            return None, error
        return models, None

    def count(self, jsonq, operator="and"):
        q = self.query(jsonq, operator, count=True)
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
        for label in fdict:
            kwargs = {label: fdict[label]}
            filters.append(Q(**kwargs))
        if filters == None:
            q = model.objects.all()
        else:
            fq = Q()
            for f in filters:
                if operator == "and":
                    fq = fq & f
                elif operator == "or":
                    fq = fq | f
            if count is False:
                q = model.objects.filter(fq)
            else:
                q = model.objects.filter(fq).count()
        return q

    def _get_app(self, appname):
        """
        returns app object
        """
        app = APPS.get_app_config(appname)
        return app

    def _get_model(self, appname, modelname):
        """
        return model
        """
        app = self._get_app(appname)
        models = app.get_models()
        model = None
        for mod in models:
            if mod.__name__ == modelname:
                model = mod
                return model
        e = Exception("Model " + modelname + " not found")
        err.new(e)
        err.check()
        return None

    def _get_models(self, app):
        """
        return models_array, error
        """
        try:
            app_models = app.get_models()
            appmods = []
            for model in app_models:
                appmods.append(model)
        except Exception as e:
            return None, str(e)
        return appmods, None

    def _count_model(self, model):
        """
        return model count, error
        """
        try:
            res = model.objects.all().count()
        except Exception as e:
            return None, str(e)
        return res, None

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
