swagger_file_content = '''
"swagger": '2.0'
info:
  description: |
    This is discovery service. Estuary-discovery service will discover the apps registered with Eureka,
    manage test sessions by communicating with estuary agents.
  version: "4.0.8"
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
    description: Estuary-discovery service will discover the apps registered with Eureka, and manage test sessions
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
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      responses:
        200:
          description: List of env vars in key value pairs
    post:
      tags:
        - estuary-discovery
      summary: Set environment variables
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: EnvVars
        in: body
        description: List of env vars by key-value pair
        required: true
        schema:
          $ref: '#/definitions/EnvVar'
      responses:
        200:
          description: Set environment variables response
        404:
          description: Set environment variables failure
  /env/{env_name}:
    get:
      tags:
        - estuary-discovery
      summary: Gets the environment variable value from the service
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: env_name
        in: path
        description: The name of the env var wanted
        required: true
        type: string
      responses:
        200:
          description: Get env var response
  /ping:
    get:
      tags:
        - estuary-discovery
      summary: Ping endpoint which replies with pong
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      responses:
        200:
          description: Ping endpoint which replies with pong. Useful for checking alive status
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
  /render/{template}/{variables}:
    get:
      tags:
        - estuary-discovery
      summary: estuary-discovery render wo env vars
      description: Gets the jinja2 rendered output from template and variable 
      produces:
        - application/json
        - text/plain
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: template
        in: path
        description: The template file
        required: true
        type: string
      - name: variables
        in: path
        description: The variables file
        required: true
        type: string
      responses:
        200:
          description: jinja2 rendered template response
        404:
          description: jinja2 rendered template failure
    post:
      tags:
        - estuary-discovery
      summary: jinja2 render where env vars can be inserted
      consumes:
        - application/json
        - application/x-www-form-urlencoded
      produces:
        - application/json
        - text/plain
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: template
        in: path
        description: Template file
        required: true
        type: string
      - name: variables
        in: path
        description: Variables file
        required: true
        type: string
      - name: EnvVars
        in: body
        description: List of env vars by key-value pair
        required: false
        schema:
          $ref: '#/definitions/EnvVar'
      responses:
        200:
          description: jinja2 rendered template response
        404:
          description: jinja2 rendered template failure
  /eurekaapps:
    get:
      tags:
        - estuary-discovery
      summary: Gets all apps registered with Eureka.
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      responses:
        200:
          description: Get apps response
        404:
          description: Get apps failure
  /eurekaapps/{type}:
    get:
      tags:
        - estuary-discovery
      summary: Gets all apps registered with Eureka with the regex 
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: type
        in: path
        description: All apps of a certain type. E.g deployer/agent/discovery/whatever. Returns empty list if nothing found.
        required: true
        type: string
      responses:
        200:
          description: Get apps response
        404:
          description: Get apps failure
  /deployments:
    get:
      tags:
        - estuary-discovery
      summary: Gets all deployments accross all estuary-deployer services.
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      responses:
        200:
          description: Get deployments response
        404:
          description: Get deployments failure
  /commandsdetached:
    get:
      tags:
        - estuary-discovery
      summary: Gets detached command info across all estuary-agents services.
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      responses:
        200:
          description: Get commands detached success
        404:
          description: Get commands detached failure
  /agents/{agent_uri}:
    get:
      tags:
        - estuary-discovery
      summary: Broadcasts/Unicasts a request to the agents connected to same Eureka domain. Useful for getting test results, starting tests ...
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: agent_uri
        in: path
        description: Broadcasts the request to the agent. E.g. /ping. 
        required: true
        type: string
      - name: IpAddr-Port
        in: header
        description: The ipAddr:port of the agent unicast target, in this format with colon. If not used, then the request will be broadcast.
        required: false
        type: string
      responses:
        200:
          description: Aggregated response from the agents, response
        404:
          description: Aggregated response from the agents, failure
  /deployers/{deployer_uri}:
    get:
      tags:
        - estuary-discovery
      summary: Broadcasts/Unicasts a request to the deployers connected to same Eureka domain. 
      produces:
        - application/json
      parameters:
      - in: header
        name: Token
        type: string
        required: false
      - name: deployer_uri
        in: path
        description: Broadcasts the request to the deployer. E.g. /ping. 
        required: true
        type: string
      - name: IpAddr-Port
        in: header
        description: The ipAddr:port of the deployer unicast target, in this format with colon. If not used, then the request will be broadcast.
        required: false
        type: string
      responses:
        200:
          description: Aggregated response from the deployers, success
        404:
          description: Aggregated response from the deployers, failure
definitions:
    EnvVar:
      type: object
      example: '{"DATABASE" : "mysql56", "IMAGE":"latest"}'
externalDocs:
  description: Find out more on github
  url: https://github.com/dinuta/estuary-discovery
'''
