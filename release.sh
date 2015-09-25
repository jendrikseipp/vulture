#! /bin/bash

set -euo pipefail

VERSION="$1"

./run-tests.sh

if [[ -n $(hg diff) ]]; then
    echo "Error: repo has uncomitted changes"
    exit 1
fi

# Bump version.
sed -i -e "s/__version__ = '.*'/__version__ = '$VERSION'/" vulture.py
if [[ -n $(hg diff) ]]; then
    hg commit -m "Update version number to $VERSION for release."
else
    echo "Version number has already been set to $VERSION"
fi
hg tag "v$VERSION"

python setup.py register
python setup.py sdist upload
