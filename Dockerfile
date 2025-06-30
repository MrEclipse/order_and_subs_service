FROM python:3.13-alpine

COPY requirements.txt /temp/requirements.txt
COPY . /app
WORKDIR /app
EXPOSE 8000

RUN apk add postgresql-client build-base postgresql-dev

RUN pip install -r /temp/requirements.txt

RUN adduser --disabled-password service-user

USER service-user
