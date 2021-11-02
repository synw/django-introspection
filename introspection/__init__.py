# flake8: noqa F401
from __future__ import absolute_import, unicode_literals
import os
from setuptools.config import read_configuration
import pkg_resources

from introspection.inspector.inspector import AppInspector
from introspection.model import ModelFieldRepresentation, ModelRepresentation


PROJECT_DIR = os.path.join(os.path.dirname(__file__), "..")


def _extract_version(package_name: str) -> str:
    """
    Get package version from installed distribution or configuration file if not
    installed
    """
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        _conf = read_configuration(os.path.join(PROJECT_DIR, "setup.cfg"))  # type: ignore
    return str(_conf["metadata"]["version"])


__version__ = _extract_version("introspection")
