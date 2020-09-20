#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#centos
docker build -t dinutac/estuary-discovery-centos:latest -f Dockerfiles/Dockerfile_centos .
docker push dinutac/estuary-discovery-centos:latest

#for alpine clean everything
git reset --hard && git clean -dfx
git checkout "${TRAVIS_BRANCH}"

#alpine
docker build . -t dinutac/estuary-discovery:latest
docker push dinutac/estuary-discovery:latest