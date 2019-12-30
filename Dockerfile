FROM alpine:3.10

RUN apk add --no-cache python

RUN apk add --no-cache \
  build-base \
  sshpass

RUN apk add --no-cache \
    bash \
    py-pip


RUN apk add --no-cache \
    python3-dev \
    libffi-dev \
    openssl-dev \
    gcc \
    libc-dev \
    make \
    curl

RUN apk add --no-cache python3 && \
    pip3 install --upgrade pip==19.3.1 setuptools==42.0.2 --no-cache

## Cleanup
RUN rm -rf /var/cache/apk/*

# Create a shared data volume
# create an empty file, otherwise the volume will
# belong to root.
RUN mkdir /data/

## Expose some volumes
VOLUME ["/data"]
VOLUME ["/variables"]

ENV TEMPLATES_DIR /data
ENV TEMPLATES_DIR_TR /data_tr

ENV VARS_DIR /variables
ENV VARS_DIR_TR /variables_tr

ENV SCRIPTS_DIR /home/dev/scripts
ENV OUT_DIR out
ENV TEMPLATE docker-compose.j2
ENV VARIABLES variables.yml

ENV TZ UTC

COPY ./ $SCRIPTS_DIR/
COPY ./inputs/templates/ $TEMPLATES_DIR/
COPY ./inputs/variables/ $VARS_DIR/

RUN pip3 install -r $SCRIPTS_DIR/requirements.txt

RUN chmod +x $SCRIPTS_DIR/*.py
RUN chmod +x $SCRIPTS_DIR/*.sh

WORKDIR /data

CMD ["python3", "/home/dev/scripts/main_flask.py"]
