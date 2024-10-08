FROM python:3.12.1 as production

# Clone prefect to a global directory so we can install editably from there; later, in
# docker-compose, we can mount your local prefect repo here to test local changes.  It's
# not _super_ important that the version here is current.
ARG INSTALL_PREFECT_VERSION 2.16.4
RUN git config --global --add safe.directory /prefect
RUN git clone https://github.com/PrefectHQ/prefect /prefect/
RUN git -C /prefect/ checkout $INSTALL_PREFECT_VERSION

RUN pip install --upgrade pip uv

COPY requirements.txt /tmp/requirements.txt
RUN uv pip install --system -r /tmp/requirements.txt
RUN uv pip install --system -e /prefect/

WORKDIR /app
COPY ./flask_task_monitoring /app/flask_task_monitoring

FROM production as testing

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN uv pip install --system -r /tmp/requirements-dev.txt

COPY ./tests /app/tests
