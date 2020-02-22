#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

# for alpine clean everything
git reset --hard && git clean -dfx
git checkout "${TRAVIS_BRANCH}"

# alpine
docker build . -t dinutac/estuary-testrunner:latest
docker push dinutac/estuary-testrunner:latest