import os

from flask_swagger_ui import get_swaggerui_blueprint

from rest.api.constants.env_constants import EnvConstants

unmodifiable_env_vars = {
    EnvConstants.TEMPLATES_DIR: os.environ.get(EnvConstants.TEMPLATES_DIR),
    EnvConstants.VARS_DIR: os.environ.get(EnvConstants.VARS_DIR),
    EnvConstants.PORT: os.environ.get(EnvConstants.PORT),
    EnvConstants.WORKSPACE: os.environ.get(EnvConstants.WORKSPACE)
}

SWAGGER_URL = '/api/docs'
API_URL = '/swagger/swagger.yml'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "estuary-discovery"
    },
)
