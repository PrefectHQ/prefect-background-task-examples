FROM python:3.12.1 as production

ARG INSTALL_PREFECT_VERSION 2.16.1
RUN git config --global --add safe.directory /prefect
RUN git clone https://github.com/PrefectHQ/prefect /prefect/
RUN git -C /prefect/ checkout $INSTALL_PREFECT_VERSION

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install -e /prefect/

WORKDIR /app
COPY ./gh_bot /app/gh_bot

FROM production as testing

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt

COPY ./tests /app/tests
