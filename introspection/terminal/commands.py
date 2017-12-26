from goerr import err
from django.conf import settings
from introspection.inspector import inspect
from term.commands import Command, rprint
import json

"""
def ls(request, cmd_args):
    path = "."
    if len(cmd_args) > 0:
        path = cmd_args[0]
    inspect.ls(path)
"""


def inspectapp(request, cmd_args):
    inspect.scanapp(cmd_args[0], term=True)
    if err.exists:
        err.new("Error inspecting app", inspectapp)
        rprint("Error scanning app", err.to_json(indent=2))
    return None


def setting_apps():
    apps = inspect.appnames
    rprint("Found", len(apps), "apps")
    for app in apps:
        rprint(app)
    return None


def setting(request, cmd_args):
    if len(cmd_args) == 0:
        return "Not enough arguments: ex: setting apps"
    if cmd_args[0] == "apps":
        return setting_apps()
    s = getattr(settings, cmd_args[0], None)
    if s is None:
        return "Setting " + cmd_args[0] + " not found"
    else:
        msg = ""
        try:
            msg = json.dumps(s, indent=2).replace(
                " ", "&nbsp;").replace("\n", "<br />")
        except:
            msg = str(s)
        rprint(msg)
        return None


c0 = Command("setting", setting, "Show a setting: ex: setting apps")
c1 = Command("inspect", inspectapp,
             "Inspect an app: ex: inspect auth")
#c2 = Command("ls", ls, "Directory listing: ex: ls templates")

COMMANDS = [c0, c1]
