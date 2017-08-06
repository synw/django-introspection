from django.conf import settings
from django.apps import apps as APPS


class Inspector:
    allowed_apps = []
    appnames = []

    def __init__(self):
        self.allowed_apps = self.apps()

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
        models, err = self.models(appname)
        if err is not None:
            return None, err
        for model in models:
            count, err = self._count_model(model)
            if err is not None:
                return None, err
            appstats[model.__name__] = count
        return appstats, None
    """
    def count(self, appname, modelname):
        model = self._get_model(appname, modelname)
        res = model.objects.all().count()
        return res
    """

    def model(self, appname, modelname):
        model, err = self._get_model(appname, modelname)
        if err is not None:
            return None, err
        count, err = self._count_model(model)
        if err is not None:
            return None, err
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
        models, err = self._get_models(app)
        if err is not None:
            return None, err
        return models, None

    def _get_app(self, appname):
        app = APPS.get_app_config(appname)
        return app

    def _get_model(self, appname, modelname):
        """
        return model, error
        """
        app = self._get_app(appname)
        models = app.get_models()
        model = None
        for mod in models:
            if mod.__name__ == modelname:
                model = mod
                return model, None
        return None, "Model " + modelname + " not found"

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
