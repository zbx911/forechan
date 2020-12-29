#!/usr/bin/env python3

from pathlib import Path

from setuptools import find_packages, setup

packages = find_packages(exclude=("tests*",))
package_data = {pkg: ("py.typed",) for pkg in packages}


setup(
    name="forechan",
    version="0.1.4",
    description="Go style CSP for Python",
    long_description=Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    author="ms-jpq",
    author_email="github@bigly.dog",
    url="https://github.com/ms-jpq/forechan",
    packages=packages,
    package_data=package_data,
)
