# you can also mount templates/variables folders for jinja2 rendering. E.g. -v $PWD/inputs/templates:/data  -v $PWD/inputs/variables:/variables
docker run  -p 8080:8080 -v $PWD/inputs/templates:/data  -v $PWD/inputs/variables:/variables -v /var/run/docker.sock:/var/run/docker.sock dinutac/estuary-discovery:latest
