#!/bin/bash

set -ex      

pip install -U pip
pip install -r ./docs/dev-requirements.txt
git config --global user.name 'CI User'
git config --global user.email '<>'

git fetch origin gh-pages:gh-pages
make -C docs deploy

if [[ -n "${DEPLOY_KEY}" && "${DRONE_BRANCH}" == "master" ]]; then 
    mkdir -p ~/.ssh/
    cp ./scripts/known_hosts ~/.ssh/
    chmod 644 ~/.ssh/known_hosts
    echo "${DEPLOY_KEY}" > ~/.ssh/id_rsa
    chmod 600 ~/.ssh/id_rsa

    git push -f ${DRONE_GIT_SSH_URL} gh-pages:gh-pages
    git push -f git@github.com:WuLiFang/Nuke.git gh-pages:gh-pages
fi
