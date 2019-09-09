import logging
import os

from flask import Flask
from flask_cors import CORS

from rest.api.definitions import swaggerui_blueprint, SWAGGER_URL
from rest.api.eureka_registrator import EurekaRegistrator
from rest.api.flask_config import Config


def create_app():
    if os.environ.get('EUREKA_SERVER'):
        EurekaRegistrator(os.environ.get('EUREKA_SERVER')).register_app(os.environ["APP_IP_PORT"])
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(Config)
    CORS(app)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    app.logger.setLevel(logging.DEBUG)
    with app.app_context():
        return app
