FROM python:3.12.1 as production

RUN ls -la /

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
COPY ./fastapi_user_signups /app/fastapi_user_signups

FROM production as testing

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install -r /tmp/requirements-dev.txt

COPY ./tests /app/tests
