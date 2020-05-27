FROM docker.io/python:3.5.9-alpine3.11
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

# We need a specific version of node
RUN for server in ipv4.pool.sks-keyservers.net keyserver.pgp.com ha.pool.sks-keyservers.net; do \
    gpg --keyserver $server --recv-keys \
      4ED778F539E3634C779C87C6D7062848A1AB005C \
      B9E2F5981AA6E0CD28160D9FF13993A75599653C \
      94AE36675C464D64BAFA68DD7434390BDBE9B9C5 \
      B9AE9905FFD7803F25714661B63B535A4C206CA9 \
      77984A986EBC2AA786BC0F66B01FBB92821C587A \
      71DCFD284A79C3B38668286BC97EC7A07EDE3FC1 \
      FD3A5288F042B6850C66B31F09FE44734EB7990E \
      8FCCA13FEF1D0C2E91008E09770F7A9A5AE15600 \
      C4F0DFFF4E8C1A8236409D08E73BC641CC11F4C8 \
      DD8F2338BAE7501E3DD5AC78C273792F7D83545D \
      A48C2BEE680E841632CD4E44F07496B3EB3C1762 && break; \
  done

RUN curl -sfSLO https://nodejs.org/dist/v8.9.3/node-v8.9.3.tar.xz && \
  curl -sfSL https://nodejs.org/dist/v8.9.3/SHASUMS256.txt.asc | gpg -d -o SHASUMS256.txt && \
  grep " node-v8.9.3.tar.xz\$" SHASUMS256.txt | sha256sum -c | grep ': OK$' && \
  tar -xf node-v8.9.3.tar.xz && \
  cd node-v8.9.3 && \
  ./configure --prefix=/usr && \
  make -j$(getconf _NPROCESSORS_ONLN) && \
  make install

RUN mkdir -p /openedx/discovery
WORKDIR /openedx/discovery
RUN wget -O - https://github.com/edx/course-discovery/tarball/open-release/ironwood.master | \
    tar xzf - --strip-components 1

# Setup nodejs requirements
RUN npm install --production
RUN ./node_modules/.bin/bower install --allow-root --production

# Replace mysql-python with mysqlclient since
# i can't find a way to build mysql-python
# RUN sed -i "s/mysql-python==1.2.5/mysqlclient/" requirements/production.txt
RUN sed -i "s/cryptography==1.7.1/cryptography/" requirements/base.txt
RUN sed -i.backup '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h

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
RUN pip install whitenoise==4.1.3

# Collect static assets
COPY ./assets.py ./course_discovery/settings/assets.py
ENV DJANGO_SETTINGS_MODULE course_discovery.settings.assets
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
COPY ./empty_dump.sql.bz2 /openedx/empty_dump.sql.bz2

COPY ./wsgi_whitenoise.py ./course_discovery/wsgi_whitenoise.py

# Patch Discovery code to fix the missing course card image in the
# Ecommerce basket page
COPY ./discovery.patch ./discovery.patch
RUN git apply discovery.patch

EXPOSE 80
CMD gunicorn \
    --bind=0.0.0.0:80 \
    --workers 2 \
    --max-requests=1000 \
    course_discovery.wsgi_whitenoise:application
