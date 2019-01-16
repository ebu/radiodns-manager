#!/usr/bin/env bash

if ! [[ $(which docker) && $(docker --version) ]]; then
    echo "Installing docker..."
    sudo apt update &&
    sudo apt install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common &&
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add - &&
    sudo add-apt-repository \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable" &&
    sudo apt update &&
    sudo apt-get install docker-ce=18.06.1~ce~3-0~ubuntu -y &&
    sudo curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose &&
    sudo chmod +x /usr/local/bin/docker-compose &&
    sudo usermod -aG docker ubuntu &&
    . ~/.profile

fi