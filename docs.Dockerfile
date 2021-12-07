FROM python:3 AS build

ARG DEBIAN_FRONTEND=noninteractive
RUN set -e
ENV LANG=C.UTF-8
ENV PYTHONIOENCODING=utf-8
# Example: https://mirrors.aliyun.com/pypi/simple
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST

WORKDIR /app/docs/

COPY ./docs/dev-requirements.txt ./
RUN pip install -U pip && \
    pip install -r ./dev-requirements.txt

COPY ./version ../
COPY ./docs/ ./
ARG SPHINXOPTS="-W"
RUN make html
