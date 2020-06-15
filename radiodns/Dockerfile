FROM python:3.8-alpine3.11
MAINTAINER Pawel Glimos <pawelglimos@gmail.com>


RUN apk update \
  && apk add --virtual  build-deps build-base gcc musl-dev linux-headers pcre-dev zlib-dev bash jpeg-dev libffi-dev libxml2-dev libxslt-dev xmlsec-dev openssl-dev py-cryptography  postgresql-dev \
  && pip install --no-cache-dir psycopg2
WORKDIR /opt/app/
COPY . /opt/app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN adduser -S --shell /bin/bash uwsgi
RUN chown -R uwsgi /usr/local/bin/python3 & \
    chown -R uwsgi /opt

USER uwsgi
CMD ["./entrypoint.sh"]
