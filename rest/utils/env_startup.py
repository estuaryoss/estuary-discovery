from rest.api.constants.env_constants import EnvConstants
from rest.environment.environment import EnvironmentSingleton


class EnvStartupSingleton:
    __instance = None
    __env = EnvironmentSingleton.get_instance()

    @staticmethod
    def get_instance():
        if EnvStartupSingleton.__instance is None:
            EnvStartupSingleton()
        return EnvStartupSingleton.__instance

    def __init__(self):
        if EnvStartupSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            EnvStartupSingleton.__instance = self

    def get_config_env_vars(self):
        return {
            EnvConstants.APP_IP: self.__env.get_env_and_virtual_env().get(
                EnvConstants.APP_IP).strip().lower() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.APP_IP) else "localhost",
            EnvConstants.PORT: int(self.__env.get_env_and_virtual_env().get(
                EnvConstants.PORT).strip()) if self.__env.get_env_and_virtual_env().get(
                EnvConstants.PORT) is not None else 8080,
            EnvConstants.EUREKA_SERVER: self.__env.get_env_and_virtual_env().get(
                EnvConstants.EUREKA_SERVER).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.EUREKA_SERVER) else None,
            EnvConstants.FLUENTD_IP_PORT: self.__env.get_env_and_virtual_env().get(
                EnvConstants.FLUENTD_IP_PORT).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.FLUENTD_IP_PORT) else None,
            EnvConstants.HTTP_AUTH_USER: self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTP_AUTH_USER).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTP_AUTH_USER) else "admin",
            EnvConstants.HTTP_AUTH_PASSWORD: self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTP_AUTH_PASSWORD).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTP_AUTH_PASSWORD) else "estuaryoss123!",
            EnvConstants.HTTPS_ENABLE: bool(self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_ENABLE).strip()) if self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_ENABLE) else False,
            EnvConstants.HTTPS_CERT: self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_CERT).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_CERT) else "https/cert.pem",
            EnvConstants.HTTPS_KEY: self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_KEY).strip() if self.__env.get_env_and_virtual_env().get(
                EnvConstants.HTTPS_KEY) else "https/key.pem"
        }
