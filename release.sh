#! /bin/bash

py.test-2.7
py.test-3.3
python setup.py register
python setup.py sdist upload
