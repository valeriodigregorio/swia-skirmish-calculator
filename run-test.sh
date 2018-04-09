#!/bin/bash
pushd src
export PYTHONPATH=`pwd`
py.test --strict -k test_
RESULT=$?
popd
exit $RESULT
