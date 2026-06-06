# Devcontainer for Python development with UV

ARG BASE_IMAGE=docker.io/python:3.14-slim-bookworm
ARG UV_IMAGE=ghcr.io/astral-sh/uv:latest
ARG JUST_IMAGE=ghcr.io/casey/just:latest

FROM ${UV_IMAGE} AS uv
FROM ${JUST_IMAGE} AS just
FROM ${BASE_IMAGE} AS system

COPY --from=uv /uv /uvx /bin/
COPY --from=just /just /usr/local/bin/

# common-utils backfills git, openssh-client, curl, zsh+oh-my-zsh.
# These are the ones no feature provides:
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    git-lfs \
    file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace