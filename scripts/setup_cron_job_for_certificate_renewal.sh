#!/usr/bin/env bash
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
elif [ -n "$1" ] && [ -n "$2" ]; then
    (crontab -l 2>/dev/null; echo "0 1 1 */2 * /home/ubuntu/radiodns-plugit/scripts/renew_certificate.sh $1 $2") | crontab -
else
    echo "Usage: <aws_credentials_file_full_path> <root_domain>" &&
    echo "example: /home/ubuntu/.aws/credentials dev.staging-radiodns.com"
fi