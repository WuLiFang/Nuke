ARG VERSION=latest
FROM natescarlet/nuke:${VERSION} as build

ARG PIP_INDEX_URL

RUN sudo -EH pip install -U pip
WORKDIR /home/nuke/src/github.com/WuLiFang/Nuke
RUN sudo chown nuke .
COPY --chown=nuke ./dev-requirements.txt ./requirements.txt ./
COPY --chown=nuke ./vendor ./vendor
COPY --chown=nuke ./Makefile ./
COPY --chown=nuke ./scripts ./scripts
RUN make .venv/lib/site-packages lib/site-packages
COPY --chown=nuke . . 

# foundry_LICENSE arg already used by base image, so we can not use.
ARG FOUNDRY_LICENSE 
ENV foundry_LICENSE=${FOUNDRY_LICENSE} 
RUN python -c 'import nuke; print(nuke.NUKE_VERSION_STRING)'
ARG SPHINXOPTS="-W"
RUN make docs/build/html
