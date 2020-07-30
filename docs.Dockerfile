ARG VERSION=latest
FROM natescarlet/nuke:${VERSION} as build

ARG PIP_INDEX_URL

# https://github.com/python-poetry/poetry/issues/2600
# https://github.com/python-poetry/poetry/issues/2711
RUN sudo -EH pip install -U pip poetry==1.1.0b2
WORKDIR /home/nuke/src/github.com/WuLiFang/Nuke
RUN sudo chown nuke .
COPY --chown=nuke ./pyproject.toml ./poetry.lock ./requirements.txt ./
COPY --chown=nuke ./vendor ./vendor
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry env use /usr/bin/python
# pendulum require poetry to install
RUN poetry run python -m pip install -U pip poetry==1.1.0b2
RUN poetry install -vv
COPY --chown=nuke ./Makefile ./
RUN make -B .venv lib/site-packages
COPY --chown=nuke . .
# skip repeat build
RUN touch .venv lib/site-packages 

# foundry_LICENSE arg already used by base image, so we can not use.
ARG FOUNDRY_LICENSE 
ENV foundry_LICENSE=${FOUNDRY_LICENSE} 
RUN python -c 'import nuke; print(nuke.NUKE_VERSION_STRING)'
ARG SPHINXOPTS="-W"
RUN make docs/build/html
