import os

from flask_swagger_ui import get_swaggerui_blueprint

unmodifiable_env_vars = {
    "TEMPLATES_DIR": os.environ.get('TEMPLATES_DIR'),
    "VARS_DIR": os.environ.get('VARS_DIR'),
    "PORT": os.environ.get('PORT'),
    "WORKSPACE": os.environ.get('WORKSPACE')
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