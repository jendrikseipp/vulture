#! /usr/bin/env python

import pathlib
import re

import setuptools


def find_version(*parts):
    here = pathlib.Path(__file__).parent
    version_file = here.joinpath(*parts).read_text()
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]$", version_file, re.M
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


with open("README.md") as f1, open("CHANGELOG.md") as f2:
    long_description = f1.read() + "\n\n" + f2.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="vulture",
    version=find_version("vulture", "version.py"),
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=install_requires,
    entry_points={"console_scripts": ["vulture = vulture.core:main"]},
    python_requires=">=3.8",
    packages=setuptools.find_packages(exclude=["tests"]),
    package_data={"vulture": ["whitelists/*.py"]},
)
