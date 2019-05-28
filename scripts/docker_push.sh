#!/bin/bash
if [[ $TRAVIS_BRANCH = "master" ]]
then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    docker_repository = "ebutech"
else
    eval $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email)
    docker_repository = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com"
fi
docker push $docker_repository/platform.open.radio &&
docker push $docker_repository/vis.open.radio &&
docker push $docker_repository/platform-proxy.open.radio &&
aws ssm send-command --document-name "AWS-RunShellScript" \
--targets Key=tag:device_group,Values=radiodns
--parameters commands="docker-compose -f docker-compose.yml down && docker-compose build --pull && docker-compose -f docker-compose.yml up" \
--region $AWS_DEFAULT_REGION
