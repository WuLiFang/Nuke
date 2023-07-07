# TODO: support Nuke12
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

WORKDIR /home/nuke/src/github.com/WuLiFang/Nuke
RUN chown nuke .

USER nuke
COPY --chown=nuke ./dev-requirements.txt ./requirements.txt ./
COPY --chown=nuke ./vendor ./vendor
COPY --chown=nuke ./Makefile ./
COPY --chown=nuke ./scripts ./scripts
RUN make .venv/.sentinel lib/site-packages/.sentinel
COPY --chown=nuke . .

RUN set -ex ;\
    . ./scripts/activate-venv.sh ;\
    ${NUKE_PYTHON} -c 'import nuke; print(nuke.NUKE_VERSION_STRING)' ;\
    pip list ;\
    ls lib/site-packages ;\
    make test
