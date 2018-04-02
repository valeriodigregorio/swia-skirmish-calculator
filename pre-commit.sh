#!/bin/bash
git stash -q --keep-index

./run-test.sh
RESULT=$?

git stash pop -q

[ $RESULT -ne 0 ] && exit 1
exit 0
