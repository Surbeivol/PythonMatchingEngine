FROM python:3.6.8-alpine

ENV APP_HOME=/home/app
ENV APP_USER=marketsim
ENV APP_UID=1000
ENV APP_GID=1000
ENV PYTHONPATH=$PYTHONPATH:$APP_HOME

RUN set -xve; \
    apk add --no-cache --update gcc gfortran python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev; \
    addgroup -S -g ${APP_GID} ${APP_USER}; \
    adduser -D -S -G ${APP_USER} -u ${APP_UID} -h ${APP_HOME} -s /bin/bash ${APP_USER};\
    chown -R ${APP_USER}:${APP_USER} ${APP_HOME} 

COPY . /



RUN pip install -U -r requirements.txt
RUN pip install pytest