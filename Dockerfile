FROM ubuntu:18.04
MAINTAINER Ioannis Noukakis <inoukakis@gmail.com>

WORKDIR /opt/test/
COPY . /opt/test/
SHELL ["/bin/bash", "-c"]
RUN apt update
RUN apt-get install -y apt-transport-https ca-certificates curl software-properties-common wget default-libmysqlclient-dev
RUN add-apt-repository ppa:jonathonf/python-3.7 -y && add-apt-repository ppa:deadsnakes/ppa -y && \
    wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
RUN apt-get update
RUN apt-get install -y python2.7 python3.7 google-chrome-stable docker-ce=18.06.1~ce~3-0~ubuntu virtualenv python-dev gcc && \
    curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \
    scripts/setup-envs.sh
CMD cd tests && \
    source venv/bin/activate && \
    python -m run.py

