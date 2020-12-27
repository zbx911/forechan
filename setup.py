#!/usr/bin/env python3

from setuptools import find_packages, setup

setup(
    name="forechan",
    version="0.1.3",
    description="Go style CSP for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ms-jpq",
    author_email="github@bigly.dog",
    url="https://github.com/ms-jpq/forechan",
    packages=find_packages(exclude=("tests*",)),
)
