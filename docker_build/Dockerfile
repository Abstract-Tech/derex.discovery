# syntax = docker/dockerfile:experimental

ARG ALPINE_VERSION=alpine3.13
ARG PYTHON_VERSION=3.6
FROM docker.io/python:${PYTHON_VERSION}-${ALPINE_VERSION} as base
MAINTAINER Chiruzzi Marco <chiruzzi.marco@gmail.com>

RUN apk add --no-cache \
    git \
    libffi-dev \
    libressl-dev \
    build-base \
    libxml2-dev \
    xmlsec-dev \
    jpeg-dev \
    zlib-dev \
    python2 \
    gnupg \
    curl

# Unfortunately this is required by mysql-python python package
# https://github.com/gliderlabs/docker-alpine/issues/181
RUN apk add mariadb-dev

ARG DISCOVERY_RELEASE=koa
ARG DISCOVERY_VERSION=open-release/koa.master
ARG DISCOVERY_REPOSITORY=https://github.com/edx/discovery.git

RUN mkdir -p /openedx/discovery
WORKDIR /openedx/discovery
RUN git clone ${DISCOVERY_REPOSITORY} --branch ${DISCOVERY_VERSION} --depth 1 /openedx/discovery

# Setup nodejs requirements
ARG NODE_VERSION=12.11.1
RUN pip install nodeenv
RUN nodeenv /openedx/discovery/nodeenv --node=${NODE_VERSION} --prebuilt
ENV PATH /openedx/discovery/nodeenv/bin:${PATH}
RUN npm install --production
RUN ./node_modules/.bin/bower install --allow-root --production

# Replace mysql-python with mysqlclient since
# i can't find a way to build mysql-python
# RUN sed -i "s/mysql-python==1.2.5/mysqlclient/" requirements/production.txt
# RUN sed -i "s/cryptography==1.7.1/cryptography/" requirements/base.txt
# RUN sed -i.backup '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h

# Setup python requirements
# TODO: Build a different image for development
RUN pip install \
    django-debug-toolbar==1.8 \
    django-elasticsearch-debug-toolbar==1.2.0 \
    transifex-client==0.12.2 \
    edx-i18n-tools \
    pyinotify==0.9.6

RUN pip install -r requirements.txt \
    --find-links http://pypi.abzt.de/alpine-3.10 \
    --trusted-host pypi.abzt.de

# By default pick the latest version
# RUN pip install whitenoise==4.1.3
ARG WHITENOISE_VERSION=
RUN pip install "whitenoise$WHITENOISE_VERSION"

COPY docker_build/derex_discovery_django/ /openedx/derex_discovery_django
RUN pip install /openedx/derex_discovery_django

# Include an already migrated mysql dump
# TODO: Remove backup from version control and
# do this step during CI build
RUN --mount=type=tmpfs,target=/mysql/var/lib/mysql \
    --mount=type=bind,from=docker.io/mysql:5.6.36,target=/mysql,rw=true \
    set -ex; \
    cp -a /dev/ /mysql; \
    export MYSQL_ALLOW_EMPTY_PASSWORD=1; \
    echo -e '[mysqld]\nport=3399\ncollation-server = utf8_general_ci\ncharacter-set-server = utf8' >> /mysql/etc/mysql/conf.d/custom_port.cnf; \
    chroot /mysql /usr/local/bin/docker-entrypoint.sh mysqld > /mysql/mysqld.out & \
    until grep "MySQL init process done. Ready for start up" /mysql/mysqld.out ; do sleep 1; done; \
    until chroot /mysql mysqladmin -P 3399 create discovery; do sleep 1; done; \
    export DJANGO_SETTINGS_MODULE="derex_discovery_django.settings.build.migration"; \
    python manage.py migrate; \
    chroot /mysql mysqldump discovery | bzip2 -9 - > /openedx/empty_dump.sql.bz2;

# Collect static assets
ENV DJANGO_SETTINGS_MODULE derex_discovery_django.settings.build.assets
RUN ./node_modules/.bin/webpack \
    --config webpack.config.js \
    --display-error-details \
    --optimize-minimize
RUN python manage.py collectstatic -v 0 --noinput

# Setup minimal yml config file, which is required by production settings
RUN echo "{}" > /openedx/config.yml
ENV DISCOVERY_CFG /openedx/config.yml

# Copy an already migrated db dump
# TODO: Remove backup from version control and
# do this step during CI build
# COPY ./empty_dump.sql.bz2 /openedx/empty_dump.sql.bz2

COPY docker_build/wsgi_whitenoise.py course_discovery/wsgi_whitenoise.py

# Patch Discovery code to fix the missing course card image in the
# Ecommerce basket page
# COPY docker_build/discovery.patch discovery.patch
# RUN git apply discovery.patch

ENV DEREX_DISCOVERY_VERSION=${DISCOVERY_RELEASE}
EXPOSE 80
CMD gunicorn \
    --bind=0.0.0.0:80 \
    --workers 2 \
    --max-requests=1000 \
    course_discovery.wsgi_whitenoise:application
