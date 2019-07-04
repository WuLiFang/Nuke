#!/bin/sh

path() {
    if [ "${OS}" = 'Windows_NT' ]; then
    echo $(cygpath -m $1)
    else 
    echo $1
    fi
}


path_list() {
    if [ "${OS}" = 'Windows_NT' ]; then
    echo $(cygpath -mp $1)
    else 
    echo $1
    fi
}


unix_path() {
    if [ "${OS}" = 'Windows_NT' ]; then
    echo $(cygpath -u $1)
    else 
    echo $1
    fi
}
