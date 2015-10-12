#!/usr/bin/env bash

# Running this script will generate Wheels for the django app and its
# dependencies

# must have setuptools and wheel library installed in the current python
# environment before running this script

# clean up previous builds
rm -rf build dist wheelhouse wheels
rm -rf *.egg-info
rm ozp-backend-wheelhouse.tar.gz

# build wheel for ozp-backend - creates wheel in dist/
python setup.py bdist_wheel

# build/collect wheels for dependencies (this will put wheels in wheelhouse/)
pip wheel -r requirements.txt

# add our wheel to the wheelhouse
cp dist/*.whl wheelhouse/

# tar up the wheelhouse
tar -czf ozp-backend-wheelhouse.tar.gz wheelhouse

# to install the backend in a new python virtualenv, run
# tar -xzf ozp-backend-wheelhouse.tar.gz
# pip install --no-index --find-links=wheelhouse ozp_backend==1.0