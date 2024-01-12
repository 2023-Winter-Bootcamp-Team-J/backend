# pull official base image
# 우분투
FROM python:3.9

# 작업 디렉토리 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DJANGO_ALLOWED_HOSTS
ARG DJANGO_SECRET_KEY
ARG DJANGO_CORS_ORIGIN_WHITELIST

ENV DJANGO_ALLOWED_HOSTS $DJANGO_ALLOWED_HOSTS
ENV DJANGO_SECRET_KEY $DJANGO_SECRET_KEY
ENV DJANGO_CORS_ORIGIN_WHITELIST $DJANGO_CORS_ORIGIN_WHITELIST

WORKDIR /
COPY requirements.txt /

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install Pillow
RUN pip install neo4j-driver
RUN pip install --upgrade django_neomodel neomodel

COPY . /
