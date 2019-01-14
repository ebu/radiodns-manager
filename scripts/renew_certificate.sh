#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
elif [ -n "$1" ] && [ -n "$2" ]; then
    export AWS_SHARED_CREDENTIALS_FILE=$1 &&
    rm -rf /etc/letsencrypt/live/$2* &&
    cd /home/ubuntu/radiodns-plugit &&
    certbot certonly -n --agree-tos --email poor@ebu.ch --dns-route53 --dns-route53-propagation-seconds 300 -d $2 -d *.$2 -d *.spi.$2 -d *.epg.$2 &&
    rm -f /home/ubuntu/radiodns-plugit/Nginx/certificates/fullchain.pem  &&
    rm -f /home/ubuntu/radiodns-plugit/Nginx/certificates/privkey.pem  &&
    cp /etc/letsencrypt/live/$2*/fullchain.pem /home/ubuntu/radiodns-plugit/Nginx/certificates/fullchain.pem &&
    cp /etc/letsencrypt/live/$2*/privkey.pem /home/ubuntu/radiodns-plugit/Nginx/certificates/privkey.pem &&
    docker-compose down &&
    docker-compose up --build -d
else
    echo "Usage: <aws_credentials_file_full_path> <root_domain>" &&
    echo "example: /home/ubuntu/.aws/credentials dev.staging-radiodns.com"
fi