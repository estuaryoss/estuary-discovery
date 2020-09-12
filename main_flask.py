#!/usr/bin/env python3

from rest.api.constants.env_constants import EnvConstants
from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.loghelpers.message_dumper import MessageDumper
from rest.api.routes import app, fluentd_service
from rest.environment.environment import EnvironmentSingleton
from rest.utils.env_startup import EnvStartupSingleton

if __name__ == "__main__":
    host = '0.0.0.0'
    port = EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.PORT)
    fluentd_tag = "startup"
    message_dumper = MessageDumper()

    if EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER):
        EurekaRegistrator(
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER)).register_app(
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.APP_IP_PORT))

    environ_dump = message_dumper.dump_message(EnvironmentSingleton.get_instance().get_env_and_virtual_env())
    ip_port_dump = message_dumper.dump_message({"host": host, "port": port})

    app.logger.debug({"msg": environ_dump})
    app.logger.debug({"msg": ip_port_dump})
    app.logger.debug({"msg": EnvStartupSingleton.get_instance().get_config_env_vars()})

    fluentd_service.emit(tag=fluentd_tag, msg=environ_dump)

    app.run(host=host, port=port)
