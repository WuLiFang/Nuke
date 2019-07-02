#!/bin/sh

. ./.env
export PYTHONPATH


if [[ ${OS} == Windows_NT ]]; then
. .venv/Scripts/activate
else
. .venv/bin/activate;
fi


