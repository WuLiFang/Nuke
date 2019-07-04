#!/bin/sh

. ./scripts/util.sh

SITE=$(./scripts/get-venv-python-lib.sh)

echo $(path ${PWD}/lib) > ${SITE}/lib.pth
echo $(path ${PWD}/lib/site-packages) >> ${SITE}/lib.pth
