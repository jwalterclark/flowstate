#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
USAGE:
  - To use the 'upload' functionality of this file, you must:>
      $ pip install twine


NOTE:
  - adapted from https://github.com/kennethreitz/setup.py/blob/master/setup.py (41b241c/2018-04-01)


TODO:
  - [ ] better integration with MANIFEST.in file content
  - [ ] move function and variables into a Class for convenient selective import


CHANGES:
  - 20180420 NGa:
    - removed need for separate 'about' variable
    - moved 'setup()' behind '__name__'-guard to allow safe import as module
    - pull package info from Pipfile
    - move basic project config variables into 'pyproject.toml'
"""


import io
import os
import sys
from configparser import ConfigParser
from json import loads as json_loads
from shutil import rmtree
from typing import List, Optional, Sequence

from setuptools import Command, find_packages, setup

# Package meta-data.
PROJECT_DIR = os.path.realpath(os.path.dirname(__file__))
project_ini_path = os.path.join(PROJECT_DIR, "pyproject.toml")
_project_conf_obj = ConfigParser()
_project_conf_obj.read(project_ini_path)
_meta = _project_conf_obj["meta"]
_path = _project_conf_obj["path"]
_missing_value = {"string": "<VALUE_NOT_SET>", "none": None}
#
PROJECT_NAME = _meta.get("name", _missing_value["string"]).strip('"')
PACKAGE_DIR = _path.get("package_dir", _missing_value["string"])
VERSION = _meta.get("version", "").strip('"')
AUTHOR = _meta.get("author", _missing_value["string"]).strip('"')
AUTHOR_EMAIL = _meta.get("author_email", _missing_value["string"]).strip('"')
MAINTAINER = _meta.get("maintainer", AUTHOR).strip('"')
MAINTAINER_EMAIL = _meta.get("maintainer_email", AUTHOR_EMAIL).strip('"')
URL = _meta.get("url", _missing_value["string"]).strip('"')
DESCRIPTION = _meta.get("description", _missing_value["string"]).strip('"')
LONG_DESCRIPTION = ""
DOWNLOAD_URL = _meta.get("download_url", _missing_value["string"]).strip('"')
# Trove classifiers
# Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = _meta.get("classifiers", "").strip('"').splitlines()
PLATFORMS = _meta.get("platforms", "").strip('"').splitlines()
LICENSE = _meta.get("license", _missing_value["string"]).strip('"')
REQUIRES_PYTHON = _meta.get("requires_python", ">= 3").strip('"')
SCRIPTS: List[str] = [] if _meta.get("scripts", None) else [
    i.strip('"') for i in _meta.get("scripts").splitlines()
]
ENTRY_POINTS__CONSOLE_SCRIPTS = (
    []
    if _meta.get("scripts", None)
    else [i.strip('"') for i in _meta.get("scripts").splitlines()]
)


# What packages are required for this module to be executed?
pkgs_ini = ConfigParser()
pkgs_ini.read("Pipfile")
REQUIRED = list(pkgs_ini["packages"])

# Import the README and use it as the long-description.
# Note: this will only work if 'README.org' is present in your MANIFEST.in file!
if not LONG_DESCRIPTION or len(LONG_DESCRIPTION) <= 0:
    with io.open(
        os.path.join(PROJECT_DIR, _project_conf_obj["path"]["readme"].strip('"')),
        encoding="utf-8",
    ) as f:
        LONG_DESCRIPTION = "\n" + f.read()


#
def prepend_to_path(opt_project_dir=True, opt_package_dir=False, opt_current_dir=False):
    if opt_current_dir and opt_current_dir not in sys.path:
        sys.path.insert(0, os.realpath(os.curdir))
    if opt_package_dir:
        sys.path.insert(0, os.path.realpath(os.path.join(PROJECT_DIR, PACKAGE_DIR)))
    if opt_project_dir:
        sys.path.insert(0, PROJECT_DIR)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = "Build and publish the package."

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print("\033[1m{0}\033[0m".format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status("Removing previous builds…")
            rmtree(os.path.join(PROJECT_DIR, "dist"))
        except OSError:
            pass

        self.status("Building Source and Wheel (universal) distribution…")
        os.system("{0} setup.py sdist bdist_wheel --universal".format(sys.executable))

        self.status("Uploading the package to PyPi via Twine…")
        os.system("twine upload dist/*")

        self.status("Pushing git tags…")
        os.system("git tag v{0}".format(VERSION))
        os.system("git push --tags")

        sys.exit()


if __name__ == "__main__":
    # Where the magic happens:
    setup(
        name=PROJECT_NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        download_url=DOWNLOAD_URL,
        classifiers=CLASSIFIERS,
        platforms=PLATFORMS,
        license=LICENSE,
        python_requires=REQUIRES_PYTHON,
        packages=find_packages(exclude=("tests",)),
        # If your package is a single module, use this instead of 'packages':
        # py_modules=['mypackage'],
        # Files to export into the system path on install.
        scripts=SCRIPTS,
        # https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html#the-console-scripts-entry-point
        entry_points={
            #'console_scripts': ['mycli=mymodule:cli']  ## EXAMPLE
            "console_scripts": ENTRY_POINTS__CONSOLE_SCRIPTS,
        },
        install_requires=REQUIRED,
        include_package_data=True,
        # $ setup.py publish support.
        cmdclass={"upload": UploadCommand,},
    )
