#!/usr/bin/env bash
rm -rf nginx/reverse_proxy/static &&
cp -a standalone_proxy/static nginx/reverse_proxy &&
docker-compose -f docker-compose-standalone.yml build &&
docker-compose -f docker-compose-standalone.yml up -d
