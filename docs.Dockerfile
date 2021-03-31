ARG VERSION=10.5v7
FROM natescarlet/nuke:${VERSION} as base

USER root
RUN set -ex ;\
    yum -y --setopt=skip_missing_names_on_install=0 install \
        make \
        gcc \
        python-devel \
        patch \
    ;\
    yum -y clean all ;\
    rm -rf /var/cache

FROM base as build

ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG foundry_LICENSE 

USER root
RUN set -ex ;\
    yum -y --setopt=skip_missing_names_on_install=0 install \
        make \
        gcc \
        python-devel \
        git \
    ;\
    yum -y clean all ;\
    rm -rf /var/cache

WORKDIR /home/nuke/src/github.com/WuLiFang/Nuke
RUN chown nuke .

USER nuke
COPY --chown=nuke ./dev-requirements.txt ./requirements.txt ./
COPY --chown=nuke ./vendor ./vendor
COPY --chown=nuke ./Makefile ./
COPY --chown=nuke ./scripts ./scripts
COPY --chown=nuke ./patches ./patches
RUN make .venv/.sentinel lib/site-packages/.sentinel
COPY --chown=nuke . .

ARG SPHINXOPTS="-W"
RUN make docs/build/html
