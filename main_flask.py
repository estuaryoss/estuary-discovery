#!/usr/bin/env python3
import os

from rest.api.constants.env_constants import EnvConstants
from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.loghelpers.message_dumper import MessageDumper
from rest.api.routes import app, fluentd_service
from rest.utils.env_startup import EnvStartup

if __name__ == "__main__":
    host = '0.0.0.0'
    port = EnvStartup.get_instance().get(EnvConstants.PORT)
    fluentd_tag = "startup"
    message_dumper = MessageDumper()

    if EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER):
        EurekaRegistrator(EnvStartup.get_instance().get(EnvConstants.EUREKA_SERVER)).register_app(
            EnvStartup.get_instance().get(EnvConstants.APP_IP_PORT))

    environ_dump = message_dumper.dump_message(dict(os.environ))
    ip_port_dump = message_dumper.dump_message({"host": host, "port": port})

    app.logger.debug({"msg": environ_dump})
    app.logger.debug({"msg": ip_port_dump})
    app.logger.debug({"msg": EnvStartup.get_instance()})

    fluentd_service.emit(tag=fluentd_tag, msg=environ_dump)

    app.run(host=host, port=port)
