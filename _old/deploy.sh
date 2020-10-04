#!/usr/bin/env bash

rm dist/*
python setup.py bdist_wheel

if [ $# -ge 1 ] && [ $1 == "test" ]; then
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
    twine upload dist/*
fi

rm -rf build