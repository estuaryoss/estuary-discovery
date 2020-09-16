#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#centos
docker build -t estuaryoss/discovery-centos:"${TRAVIS_TAG}" -f Dockerfiles/Dockerfile_centos .
docker push estuaryoss/discovery-centos:"${TRAVIS_TAG}"

#for alpine clean everything
#git reset --hard && git clean -dfx
#git checkout tags/"${TRAVIS_TAG}" -b "${TRAVIS_TAG}"

#alpine
#docker build . -t estuaryoss/discovery:"${TRAVIS_TAG}"
#docker push estuaryoss/discovery:"${TRAVIS_TAG}"