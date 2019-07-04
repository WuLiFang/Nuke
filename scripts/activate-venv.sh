#!/bin/sh

. ./scripts/util.sh

if [ -f ./.env ]; then . ./.env ;fi


if [ "${OS}" = 'Windows_NT' ]; then
export PYTHONPATH=$(path_list "${PYTHONPATH}:${PWD}/lib:${PWD}/lib/site-pacakages")
. .venv/Scripts/activate
else
export PYTHONPATH="${PYTHONPATH}:${PWD}/lib:${PWD}/lib/site-pacakages"
. .venv/bin/activate;
fi

PYTHON_LIB=$(./scripts/get-python-lib.sh)
