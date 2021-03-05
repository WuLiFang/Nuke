# TODO: support Nuke12
ARG VERSION=10.5v7
FROM natescarlet/nuke:${VERSION}

USER root
RUN set -ex ;\
    yum -y --setopt=skip_missing_names_on_install=0 install \
        make \
        gcc \
        python-devel \
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

# foundry_LICENSE arg already used by base image, so we can not use.
ARG FOUNDRY_LICENSE 
ENV foundry_LICENSE=${FOUNDRY_LICENSE}
RUN set -ex ;\
    . ./scripts/activate-venv.sh ;\
    ${NUKE_PYTHON} -c 'import nuke; print(nuke.NUKE_VERSION_STRING)' ;\
    pip list ;\
    ls lib/site-packages ;\
    make test
