#! /bin/bash

set -euo pipefail

VERSION="$1"

# Check dependencies.
twine -h

tox

# Check that NEWS file is up-to-date.
grep "$VERSION" NEWS.rst || echo "Version $VERSION missing in NEWS file."

# Check for uncommited changes.
set +e
git diff --quiet && git diff --cached --quiet
retcode=$?
set -e
if [[ $retcode != 0 ]]; then
    echo "There are uncommited changes:"
    git status
    exit 1
fi

git pull

# Bump version.
sed -i -e "s/__version__ = '.*'/__version__ = '$VERSION'/" vulture/core.py
git commit -am "Update version number to ${VERSION} for release."
git tag -a "v$VERSION" -m "v$VERSION" HEAD

python setup.py sdist bdist_wheel
twine upload dist/vulture-${VERSION}.tar.gz dist/vulture-${VERSION}-py2.py3-none-any.whl

git push
git push --tags
