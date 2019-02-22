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
--targets Key=tag:Name,Values=radiodns \
--parameters commands="eval $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email) && \
cd $ROOT_FOLDER && docker-compose -f docker-compose.yml down && \
docker image rm $DOCKER_REPOSITORY/platform.open.radio && \
docker-compose -f docker-compose.yml build && \
docker-compose -f docker-compose.yml up -d" \
--region $AWS_DEFAULT_REGION --timeout-seconds 300
aws ssm send-command --document-name "AWS-RunShellScript" \
--targets Key=tag:Name,Values=radiovis \
--parameters commands="eval $(aws ecr get-login --region $AWS_DEFAULT_REGION --no-include-email) && \
cd $ROOT_FOLDER && docker-compose -f docker-compose-radiovis-prod.yml down && \
docker image rm $DOCKER_REPOSITORY/vis.open.radio && \
docker-compose -f docker-compose-radiovis-prod.yml build && \
docker-compose -f docker-compose-radiovis-prod.yml up -d" \
--region $AWS_DEFAULT_REGION --timeout-seconds 300

