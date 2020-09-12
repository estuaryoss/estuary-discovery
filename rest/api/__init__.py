import logging

from flask import Flask
from flask_cors import CORS

from rest.api.definitions import swaggerui_blueprint, SWAGGER_URL
from rest.api.flask_config import Config


class AppCreatorSingleton:
    __instance = None
    __app = None

    @staticmethod
    def get_instance():
        if AppCreatorSingleton.__instance is None:
            AppCreatorSingleton()
        return AppCreatorSingleton.__instance

    def __init__(self):
        """ The constructor. This class gets a single flask app """
        self.app = Flask(__name__, instance_relative_config=False)
        self.app.config.from_object(Config)
        CORS(self.app)
        self.app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
        self.app.logger.setLevel(logging.DEBUG)

        if AppCreatorSingleton.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            AppCreatorSingleton.__instance = self

    def get_app(self):
        with self.app.app_context():
            return self.app
