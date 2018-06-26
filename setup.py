#! /usr/bin/env python

import codecs
import os.path
import re
import sys

import setuptools
from setuptools.command.test import test as TestCommand


def read(*parts):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as f:
        return f.read()


def find_version(*file_parts):
    version_file = read(*file_parts)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]$", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)

        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        sys.exit(pytest.main(self.test_args))


setuptools.setup(
    name='vulture',
    version=find_version('vulture', 'core.py'),
    description='Find dead code',
    long_description='\n\n'.join(
        [open('README.rst').read(), open('NEWS.rst').read()]),
    keywords='dead-code-removal',
    author='Jendrik Seipp',
    author_email='jendrikseipp@gmail.com',
    url='https://github.com/jendrikseipp/vulture',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Quality Assurance'
    ],
    entry_points={
        'console_scripts': ['vulture = vulture.core:main'],
    },
    tests_require=['pytest', 'pytest-cov'],
    cmdclass={'test': PyTest},
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={'vulture': ['whitelists/*.py']},
)
