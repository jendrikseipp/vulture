#! /usr/bin/env python

import codecs
import os.path
import re

import setuptools


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), "r") as f:
        return f.read()


def find_version(*file_parts):
    version_file = read(*file_parts)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]$", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md") as f1, open("CHANGELOG.md") as f2:
    long_description = f1.read() + "\n\n" + f2.read()

setuptools.setup(
    name="vulture",
    version=find_version("vulture", "core.py"),
    description="Find dead code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="dead-code-removal",
    author="Jendrik Seipp",
    author_email="jendrikseipp@gmail.com",
    url="https://github.com/jendrikseipp/vulture",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={"console_scripts": ["vulture = vulture.core:main"]},
    python_requires=">=3.6",
    packages=setuptools.find_packages(exclude=["tests"]),
    package_data={"vulture": ["whitelists/*.py"]},
)
