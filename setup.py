#! /usr/bin/env python

import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

from vulture import __version__


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)

        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        sys.exit(pytest.main(self.test_args))


setup(
    name='vulture',
    version=__version__,
    description='Find dead code',
    long_description='\n\n'.join(
        [open('README.txt').read(), open('NEWS.txt').read()]),
    keywords='vulture dead unused code pyflakes',
    author='Jendrik Seipp',
    author_email='jendrikseipp@web.de',
    url='https://bitbucket.org/jendrikseipp/vulture',
    license='MIT',
    py_modules=['vulture'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Quality Assurance'
    ],
    entry_points={
        'console_scripts': ['vulture = vulture:main'],
    },
    tests_require=['pytest', 'pytest-cov'],
    cmdclass={'test': PyTest},
)
