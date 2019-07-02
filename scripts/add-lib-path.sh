#!/bin/sh

SITE=$(./scripts/get-python-lib.sh)

path() {
    if [ "${OS}" = 'Windows_NT' ]; then
    echo $(cygpath -w $1)
    else 
    echo $1
    fi
}

echo $(path ${PWD}/lib) > ${SITE}/lib.pth
echo $(path ${PWD}/lib/site-packages) >> ${SITE}/lib.pth
