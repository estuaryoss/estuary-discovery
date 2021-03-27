FROM centos:8

ENV TZ UTC
ENV PORT 8080
ENV SCRIPTS_DIR /root/app
ENV HTTPS_DIR /root/app/https
ENV WORKSPACE $SCRIPTS_DIR
ENV TEMPLATES_DIR $WORKSPACE/templates
ENV VARS_DIR $WORKSPACE/variables

WORKDIR $SCRIPTS_DIR

COPY inputs/templates/ $TEMPLATES_DIR/
COPY inputs/variables/ $VARS_DIR/

COPY dist/main_flask $SCRIPTS_DIR/main-linux
COPY https/key.pem $HTTPS_DIR/
COPY https/cert.pem $HTTPS_DIR/

RUN chmod +x $SCRIPTS_DIR/main-linux

CMD ["/root/app/main-linux"]
