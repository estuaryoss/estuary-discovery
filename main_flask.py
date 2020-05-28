#!/usr/bin/env python3
import os

from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.logginghelpers.message_dumper import MessageDumper
from rest.api.routes import app, fluentd_utils
from rest.utils.env_startup import EnvStartup

if __name__ == "__main__":
    host = '0.0.0.0'
    port = EnvStartup.get_instance().get("port")
    fluentd_tag = "startup"
    message_dumper = MessageDumper()

    if EnvStartup.get_instance().get("eureka_server"):
        EurekaRegistrator(EnvStartup.get_instance().get("eureka_server")).register_app(
            EnvStartup.get_instance().get("app_ip_port"))

    environ_dump = message_dumper.dump_message(dict(os.environ))
    ip_port_dump = message_dumper.dump_message({"host": host, "port": port})

    app.logger.debug({"msg": environ_dump})
    app.logger.debug({"msg": ip_port_dump})
    app.logger.debug({"msg": EnvStartup.get_instance()})

    fluentd_utils.emit(tag=fluentd_tag, msg=environ_dump)

    app.run(host=host, port=port)
