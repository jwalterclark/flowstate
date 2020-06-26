#!/bin/false
# -*- coding: utf-8 -*-
from __future__ import print_function

#
import os
import sys
from logging import Logger

#
from invoke import Collection, task

log = Logger(__name__)


# create variable for 'root' namespace, notably creating a 'root' namespace inhibits implicitly importing task functions
ns = Collection()


@task
def clean(c):
    c.run("git clean -df")


@task
def test(c):
    c.run("pipenv run pytest")


@task
def check(c):
    c.run("pipenv run pre-commit")


@task
def stage(c):
    c.run("git add --all")


@task
def build(c):
    c.run("pipenv run python setup.py build")


# EOF
