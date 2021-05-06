#!/bin/bash

echo "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

#compile
pip3 install -r requirements.txt
pyinstaller --onefile --clean main.py

#centos
docker build -t estuaryoss/discovery:latest -f Dockerfile .
docker push estuaryoss/discovery:latest