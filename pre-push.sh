#!/bin/bash
git stash -q --keep-index
sh run-test.sh
RESULT=$?
git stash pop -q
exit $RESULT
