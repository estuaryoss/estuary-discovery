#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#centos
docker build -t estuaryoss/discovery:"${TRAVIS_TAG}" -f Dockerfile .
docker push estuaryoss/discovery:"${TRAVIS_TAG}"

#for alpine clean everything
git reset --hard && git clean -dfx
git checkout tags/"${TRAVIS_TAG}" -b "${TRAVIS_TAG}"
