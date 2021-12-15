#!/usr/bin/env python3
import sys

from rest.api.constants.env_constants import EnvConstants
from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.loghelpers.message_dumper import MessageDumper
from rest.api.routes import app, fluentd_service
from rest.environment.environment import EnvironmentSingleton
from rest.utils.env_startup import EnvStartupSingleton

if __name__ == "__main__":
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None

    port = EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.PORT)
    message_dumper = MessageDumper()
    host = '0.0.0.0'
    fluentd_tag = "startup"

    if EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER):
        EurekaRegistrator(
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.EUREKA_SERVER)).register_app(
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.APP_IP),
            EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.PORT))

    environ_dump = message_dumper.dump_message(EnvironmentSingleton.get_instance().get_env_and_virtual_env())
    ip_port_dump = message_dumper.dump_message({"host": host, "port": port})

    app.logger.debug({"msg": environ_dump})
    app.logger.debug({"msg": ip_port_dump})
    app.logger.debug({"msg": EnvStartupSingleton.get_instance().get_config_env_vars()})

    fluentd_service.emit(tag=fluentd_tag, msg=environ_dump)

    is_https = EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.HTTPS_ENABLE)
    https_cert_path = EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.HTTPS_CERT)
    https_prv_key_path = EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.HTTPS_KEY)
    ssl_context = None
    if is_https:
        ssl_context = (https_cert_path, https_prv_key_path)
    app.run(host=host, port=port, ssl_context=ssl_context)
