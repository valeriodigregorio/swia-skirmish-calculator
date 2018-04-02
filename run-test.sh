#!/bin/bash

export PYTHONPATH=`pwd`
py.test --strict -k test_
