#!/bin/bash
# usage: [major, minor, patch] "commit message"
poetry version $1
git add .
git commit -m "$2"
git push
NEW_VERSION=`poetry version -s`
git tag v${NEW_VERSION}
git push origin v${NEW_VERSION}
PYPI_TOKEN=`echo "op://Private/pypi.org/api_token" | op inject`
poetry publish --build --username __token__ --password PYPI_TOKEN
