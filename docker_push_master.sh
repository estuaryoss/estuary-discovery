#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#centos
docker build -t estuaryoss/discovery-centos:latest -f Dockerfile_centos .
docker push estuaryoss/discovery-centos:latest

#for alpine clean everything
git reset --hard && git clean -dfx
git checkout "${TRAVIS_BRANCH}"

#alpine
docker build . -t estuaryoss/discovery:latest
docker push estuaryoss/discovery:latest