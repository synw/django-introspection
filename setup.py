from os import path
from setuptools import setup, find_packages


version = __import__("introspection").__version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="django-introspection",
    packages=find_packages(),
    include_package_data=True,
    version=version,
    description="Introspection tools for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="synw",
    author_email="synwe@yahoo.com",
    url="https://github.com/synw/django-introspection",
    download_url="https://github.com/synw/django-introspection/releases/tag/" + version,
    keywords=["django"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django :: 3.0",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    zip_safe=False,
)
