#!/usr/bin/env bash
sudo apt-get update &&
sudo apt-get install software-properties-common -y &&
sudo add-apt-repository ppa:certbot/certbot -y &&
sudo apt-get update &&
sudo apt-get install certbot python3-pip -y &&
pip3 install certbot-dns-route53 &&
certbot plugins
