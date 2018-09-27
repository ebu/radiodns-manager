FROM python:2.7-jessie
MAINTAINER Ioannis Noukakis <inoukakis@gmail.com>

COPY . /opt/app/
WORKDIR /opt/app/

RUN apt-get update && apt-get install -y python-dev libmysqlclient-dev
RUN pip install .

CMD python server.py