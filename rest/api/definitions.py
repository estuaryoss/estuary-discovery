import os

from flask_swagger_ui import get_swaggerui_blueprint

env_vars = {
    "TEMPLATES_DIR": os.environ.get('TEMPLATES_DIR'),
    "VARS_DIR": os.environ.get('VARS_DIR'),
    "TEMPLATE": os.environ.get('TEMPLATE'),
    "VARIABLES": os.environ.get('VARIABLES'),
    "TEMPLATES_DIR_FILES": os.listdir(os.environ.get('TEMPLATES_DIR')),
    "VARS_DIR_FILES": os.listdir(os.environ.get('VARS_DIR')),
    "PATH": os.environ.get('PATH')
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

swagger_file_content = '''
"swagger": '2.0'
info:
  description: |
    This is estuary-discovery service. Estuary-discovery service will discover the apps registered with Eureka.
  version: "2.0.0"
  title: estuary-discovery
  termsOfService: http://swagger.io/terms/
  contact:
    email: constantin.dinuta@gmail.com
  license:
    name: Apache 2.0
    url: http://www.apache.org/licenses/LICENSE-2.0.html
# host: localhost:8080
basePath: /
tags:
  - name: estuary-discovery
    description: Estuary-discovery service will discover the apps registered with Eureka.
    externalDocs:
      description: Find out more on github
      url: https://github.com/dinuta/estuary-discovery
schemes:
  - http
paths:
  /env:
    get:
      tags:
        - estuary-discovery
      summary: Print env vars
      produces:
        - application/json
      responses:
        200:
          description: List of env vars in key value pairs
  /ping:
    get:
      tags:
        - estuary-discovery
      summary: Ping endpoint which replies with pong
      produces:
        - application/json
      responses:
        200:
          description: Ping endpoint which replies with pong. Useful for situations where checking the alive status of the service is needed.
  /about:
    get:
      tags:
        - estuary-discovery
      summary: Information about the application.
      produces:
        - application/json
      responses:
        200:
          description: Prints the name, version of the estuary-discovery application.
  /rend/{template}/{variables}:
    get:
      tags:
        - estuary-discovery
      summary: estuary-discovery render wo env vars
      description: Gets the rendered output from template and variable files with estuary-discovery
      produces:
        - application/json
        - text/plain
      parameters:
        - name: template
          in: path
          description: The template file mounted in docker
          required: true
          type: string
        - name: variables
          in: path
          description: The variables file mounted in docker
          required: true
          type: string
      responses:
        200:
          description: estuary-discovery rendered template with jinja2
        404:
          description: estuary-discovery failure to rend the template
  /rendwithenv/{template}/{variables}:
    post:
      tags:
        - estuary-discovery
      summary: estuary-discovery render with inserted env vars
      consumes:
        - application/json
        - application/x-www-form-urlencoded
      produces:
        - application/json
        - text/plain
      parameters:
        - name: template
          in: path
          description: Template file mounted in docker
          required: true
          type: string
        - name: variables
          in: path
          description: Variables file mounted in docker
          required: true
          type: string
        - name: EnvVars
          in: body
          description: List of env vars by key-value pair
          required: false
          schema:
            $ref: '#/definitions/envvar'
      responses:
        200:
          description: estuary-discovery rendered template with jinja2
        404:
          description: estuary-discovery failure to rend the template
  /getenv/{env_name}:
    get:
      tags:
        - estuary-discovery
      summary: Gets the environment variable value from the estuary-discovery container
      produces:
        - application/json
      parameters:
      - name: env_name
        in: path
        description: The name of the env var wanted
        required: true
        type: string
      responses:
        200:
          description: Get env var success
        404:
          description: Get env var failure
  /geteurekaapps:
    get:
      tags:
        - estuary-discovery
      summary: Gets all apps registered with Eureka.
      produces:
        - application/json
      responses:
        200:
          description: Get apps success
        404:
          description: Get apps failure
  /geteurekaapps/{type}:
    get:
      tags:
        - estuary-discovery
      summary: Gets all apps registered with Eureka.
      produces:
        - application/json
      parameters:
        - name: type
          in: path
          description: All apps of a certain type. E.g estuary-deployer/estuary-testrunner/estuary-discovery/whatever. Returns empty list if nothing found.
          required: true
          type: string
      responses:
        200:
          description: Get apps success
        404:
          description: Get apps failure
  /getdeployments:
    get:
      tags:
        - estuary-discovery
      summary: Gets all deployments accross all estuary-deployer services.
      produces:
        - application/json
      responses:
        200:
          description: Get deployments success
        404:
          description: Get deployments failure
  /gettests:
    get:
      tags:
        - estuary-discovery
      summary: Gets all tests accross all estuary-testrunners services.
      produces:
        - application/json
      responses:
        200:
          description: Get tests success
        404:
          description: Get tests failure
  /testrunner/{testrunner_uri}:
    get:
      tags:
        - estuary-discovery
      summary: Broadcasts/Unicasts a request to the testrunners connected to same Eureka domain. Useful for getting test results, starting tests ...
      produces:
        - application/json
      parameters:
        - name: testrunner_uri
          in: path
          description: Broadcasts the request to the testrunner. E.g. /ping. 
          required: true
          type: string
        - name: IpAddr-Port
          in: header
          description: The ipAddr:port of the testrunner unicast target, in this format with colon. If not used, then the request will be broadcast.
          required: false
          type: string
      responses:
        200:
          description: Aggregated response from the testrunners, success
        404:
          description: Aggregated response from the testrunners, failure
definitions:
    envvar:
      type: object
      example: '{"DATABASE" : "mysql56", "IMAGE":"latest"}'
externalDocs:
  description: Find out more on github
  url: https://github.com/dinuta/estuary-discovery
'''
