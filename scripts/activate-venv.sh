#!/bin/sh

if [ -f ./.env ]; then . ./.env ;fi


if [ "${OS}" = 'Windows_NT' ]; then
export PYTHONPATH="${PYTHONPATH};${PWD}/lib;${PWD}/lib/site-pacakages"
. .venv/Scripts/activate
else
export PYTHONPATH="${PYTHONPATH}:${PWD}/lib:${PWD}/lib/site-pacakages"
. .venv/bin/activate;
fi

PYTHON_LIB=$(python -c 'from distutils import sysconfig;print(sysconfig.get_python_lib())')

