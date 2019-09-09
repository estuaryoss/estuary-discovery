@echo off
REM you can also mount templates/variables folders for jinja2 rendering. E.g. -v %CD%/inputs/templates:/data  -v %CD%/inputs/variables:/variables
docker run  -p 8080:8080  -v /var/run/docker.sock:/var/run/docker.sock dinutac/estuary-discovery:latest
