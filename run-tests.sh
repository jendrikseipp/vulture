#! /bin/bash

set -euo pipefail

pep8 .

pyflakes .

py.test

# Check vulture for dead code with vulture.
./vulture.py vulture.py whitelist.py

# Install with: sudo pip install -U collective.checkdocs
# Alternative: python setup.py --long-description | \
#              rst2html.py --exit-status 2 > output.html
python setup.py checkdocs
