#! /bin/bash

set -exuo pipefail

VERSION="$1"
CHANGES="/tmp/vulture-$VERSION-changes"

cd "$(dirname ${0})/../"

# Check dependencies.
hub --version > /dev/null
tox --version > /dev/null
twine -h > /dev/null

# Check for uncommitted changes.
set +e
git diff --quiet && git diff --cached --quiet
retcode=$?
set -e
if [[ $retcode != 0 ]]; then
    echo "There are uncommitted changes:"
    git status
    exit 1
fi

git pull

tox

# Bump version.
sed -i -e "s/__version__ = \".*\"/__version__ = \"$VERSION\"/" vulture/version.py
git commit -am "Update version number to ${VERSION} for release."
git tag -a "v$VERSION" -m "v$VERSION" HEAD

python3 setup.py sdist bdist_wheel --universal
twine upload dist/vulture-${VERSION}.tar.gz dist/vulture-${VERSION}-py2.py3-none-any.whl

git push
git push --tags

# Add changelog to Github release.
./dev/make-release-notes.py "$VERSION" CHANGELOG.md "$CHANGES"
hub release create v"$VERSION" --file="$CHANGES"
