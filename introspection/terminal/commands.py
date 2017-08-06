from django.conf import settings
from introspection.inspector import inspect
from terminal.commands import Command, rprint


def inspectapp(request, cmd_args):
    num_args = len(cmd_args)
    if num_args != 1:
        return "The app name is required: ex: models auth"
    has_model = "." in cmd_args[0]
    if has_model is False:
        appname = cmd_args[0]
        stats, err = inspect.app(appname)
        if err is not None:
            return err
        for modelname in stats:
            rprint("<b>" + modelname + "</b>", ": found",
                   stats[modelname], "instances")
        return None
    else:
        path = cmd_args[0]
        s = path.split(".")
        appname = s[0]
        modelname = s[1]
        infos, err = inspect.model(appname, modelname)
        if err is not None:
            return err
        rprint("Found", len(infos["fields"]), "fields:")
        for field in infos["fields"]:
            name = "<b>" + field["name"] + "</b>"
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
            rprint("Found", len(infos["relations"]), "external", relstr, ":")
            for rel in infos["relations"]:
                name = "<b>" + rel["field"] + "</b>"
                relname = rel["related_name"]
                relfield = rel["relfield"]
                relstr = ""
                if relname is not None:
                    relstr = "with related name " + relname
                rprint(name, "from", relfield, rel["type"], relstr)
        rprint("Found", infos["count"], "instances of", modelname)
    return None


def setting_apps():
    apps = inspect.apps()
    rprint("Found", len(apps), "apps")
    for app in apps:
        rprint(app)
    return None


def setting(request, cmd_args):
    if len(cmd_args) == 0:
        return "Not enough arguments: ex: setting apps"
    if cmd_args[0] == "apps":
        return setting_apps()
    if cmd_args[0] in settings:
        return settings[cmd_args[0]]
    a = "arguments"
    if len(cmd_args) == 1:
        a = "argument"
    cmd_argslist = " ".join(cmd_args)
    err = "Unknown " + a + " " + cmd_argslist
    return err


c0 = Command("setting", setting, "Show a setting: ex: setting apps")
c1 = Command("inspect", inspectapp,
             "Inspect an app: ex: inspect auth")

COMMANDS = [c0, c1]
