import py_eureka_client.eureka_client as eureka_client

from about import properties
from rest.api.constants.env_constants import EnvConstants
from rest.utils.env_startup import EnvStartupSingleton


class EurekaRegistrator:

    def __init__(self, host):
        self.host = host

    def register_app(self, app_ip, app_port):
        print("Starting eureka register on eureka server {}. \n".format(self.host))
        print("{} registering with: ip={}, port={} \n".format(properties['name'], app_ip, app_port))

        protocol = "https" if EnvStartupSingleton.get_instance().get_config_env_vars().get(EnvConstants.HTTPS_ENABLE) \
            else "http"

        eureka_client.init(eureka_server=f"{self.host}",
                           app_name=f"{properties['name']}",
                           instance_port=app_port,
                           instance_secure_port=app_port,
                           instance_ip=app_ip,
                           home_page_url=f"{protocol}://{app_ip}:{app_port}/",
                           health_check_url=f"{protocol}://{app_ip}:{app_port}/ping",
                           status_page_url=f"{protocol}://{app_ip}:{app_port}/ping"
                           )
