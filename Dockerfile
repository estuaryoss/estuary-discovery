FROM alpine:3.11

RUN apk add --no-cache python3 bash curl && \
    pip3 install --upgrade pip==20.1.1 setuptools==46.2.0 --no-cache

RUN apk add --no-cache \
    python3-dev \
    libffi-dev \
    openssl-dev \
    gcc \
    libc-dev \
    make

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
ENV HTTP_AUTH_TOKEN None
ENV PORT 8080

ENV VARS_DIR /variables

ENV SCRIPTS_DIR /scripts
ENV OUT_DIR out
ENV TEMPLATE docker-compose.j2
ENV VARIABLES variables.yml

ENV TZ UTC

COPY ./ $SCRIPTS_DIR/
COPY ./inputs/templates/ $TEMPLATES_DIR/
COPY ./inputs/variables/ $VARS_DIR/

RUN chmod +x $SCRIPTS_DIR/*.py
RUN chmod +x $SCRIPTS_DIR/*.sh

WORKDIR $SCRIPTS_DIR

RUN pip3 install -r $SCRIPTS_DIR/requirements.txt
RUN pip3 install uwsgi

CMD ["uwsgi", "/scripts/flaskconfig.ini"]