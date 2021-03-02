ARG VERSION=latest
FROM natescarlet/nuke:${VERSION}

USER root
RUN set -ex ;\
    yum -y --setopt=skip_missing_names_on_install=0 install \
        make \
        gcc \
        python27-python-devel \
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
RUN make .venv/lib/site-packages lib/site-packages
COPY --chown=nuke . . 

# foundry_LICENSE arg already used by base image, so we can not use.
ARG FOUNDRY_LICENSE 
ENV foundry_LICENSE=${FOUNDRY_LICENSE} 
RUN python -c 'import nuke; print(nuke.NUKE_VERSION_STRING)'
RUN make test
