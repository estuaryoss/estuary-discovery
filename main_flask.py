#!/usr/bin/env python3
import os

from about import properties
from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.logginghelpers.message_dumper import MessageDumper
from rest.api.routes import app, fluentd_utils

if __name__ == "__main__":
    host = '0.0.0.0'
    port = properties["port"]
    fluentd_tag = "startup"
    message_dumper = MessageDumper()

    if os.environ.get('PORT'):
        port = int(os.environ.get("PORT"))  # override port  if set from env

    if os.environ.get('EUREKA_SERVER'):
        EurekaRegistrator(os.environ.get('EUREKA_SERVER')).register_app(os.environ["APP_IP_PORT"])

    environ_dump = message_dumper.dump_message(dict(os.environ))
    ip_port_dump = message_dumper.dump_message({"host": host, "port": port})

    app.logger.debug({"msg": environ_dump})
    app.logger.debug({"msg": ip_port_dump})

    fluentd_utils.debug(fluentd_tag, environ_dump)

    app.run(host=host, port=port)
