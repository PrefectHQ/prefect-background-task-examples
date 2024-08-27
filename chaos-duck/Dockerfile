FROM python:3.12.1 AS production

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

ENV UV_SYSTEM_PYTHON=1

ARG INSTALL_PREFECT_VERSION=3.0.0rc19
RUN git config --global --add safe.directory /prefect
RUN git clone https://github.com/PrefectHQ/prefect /prefect/
RUN git -C /prefect/ checkout $INSTALL_PREFECT_VERSION

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install -r /tmp/requirements.txt

RUN uv pip install -e /prefect/

WORKDIR /app
COPY ./chaos_duck /app/chaos_duck

FROM production AS testing

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN uv pip install -r /tmp/requirements-dev.txt

COPY ./tests /app/tests