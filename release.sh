#! /bin/bash

tox
python setup.py register
python setup.py sdist upload
