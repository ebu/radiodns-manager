#!/bin/bash
if [[ $TRAVIS_BRANCH = "master" ]]
then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
else
    eval $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)
fi
docker push $DOCKER_REPOSITORY/platform.open.radio
docker push $DOCKER_REPOSITORY/vis.open.radio
docker push $DOCKER_REPOSITORY/platform-proxy.open.radio
aws ssm send-command --document-name "AWS-RunShellScript" \
--targets Key=tag:device_group,Values=radiodns \
--parameters commands="docker-compose -f docker-compose-ebu-io.yml down && docker-compose build --pull && docker-compose -f docker-compose-ebu-io.yml up" \
--region $AWS_DEFAULT_REGION
