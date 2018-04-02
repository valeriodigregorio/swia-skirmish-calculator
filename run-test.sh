#!/bin/bash
pushd src
export PYTHONPATH=`pwd`
py.test --strict -k test_
popd
