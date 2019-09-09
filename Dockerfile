FROM alpine:3.9.4

RUN apk add --no-cache python

RUN apk add --no-cache \
  build-base \
  sshpass

RUN apk add --no-cache \
    bash \
    py-pip


RUN apk add --no-cache \
    python-dev \
    libffi-dev \
    openssl-dev \
    gcc \
    libc-dev \
    make

RUN apk add --no-cache python3 && \
    pip3 install --upgrade pip setuptools --no-cache

RUN pip3 install \
  PyYAML \
  httplib2 \
  urllib3 \
  simplejson \
  Jinja2 \
  jinja2-cli \
  flask \
  flask_restplus\
  jsonify \
  parameterized \
  flask_swagger_ui \
  requests \
  requests_toolbelt \
  flask-cors \
  py_eureka_client

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

ADD ./ $SCRIPTS_DIR/
ADD ./inputs/templates/ $TEMPLATES_DIR/
ADD ./inputs/variables/ $VARS_DIR/


RUN chmod +x $SCRIPTS_DIR/*.py
RUN chmod +x $SCRIPTS_DIR/*.sh

WORKDIR /data

CMD ["python3", "/home/dev/scripts/main_flask.py"]
