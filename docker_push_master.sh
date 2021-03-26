#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#centos
docker build -t estuaryoss/discovery:latest -f Dockerfile .
docker push estuaryoss/discovery:latest

#for alpine clean everything
git reset --hard && git clean -dfx
git checkout "${TRAVIS_BRANCH}"