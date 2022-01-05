<h1 align="center"><img src="./docs/images/banner_discovery.png" alt="Testing as a service"></h1>

## Estuary Discovery

Estuary Discovery service. Aggregator of the Estuary-Stack.

- Reads the apps/services registered in Eureka
- Reads the commands from Estuary-Agent(s) registered in Eureka
- Sends L7 HTTP messages (commands/environment set & read / file transfers) to the Agents

## Coverage & code quality

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/fc69b90ee90546158876e5344d9c2af2)](https://www.codacy.com/gh/estuaryoss/estuary-discovery?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=estuaryoss/estuary-discovery&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/c0894a0a9785a3fb7afc/maintainability)](https://codeclimate.com/github/estuaryoss/estuary-discovery/maintainability)

## Linux status

[![Build Status](https://travis-ci.com/estuaryoss/estuary-discovery.svg?token=UC9Z5nQSPmb5vK5QLpJh&branch=master)](https://travis-ci.com/estuaryoss/estuary-discovery)

## Windows status

[![CircleCI](https://circleci.com/gh/estuaryoss/estuary-discovery.svg?style=svg)](https://circleci.com/gh/estuaryoss/estuary-discovery)

## Docker Hub

[alpine](https://hub.docker.com/r/estuaryoss/discovery) ![](https://img.shields.io/docker/pulls/estuaryoss/discovery.svg)

## Api docs

[4.2.4](https://app.swaggerhub.com/apis/dinuta/estuary-discovery/4.2.4)

## Postman collection

The Postman collection is located in **docs** folder.

## Service HTTP GET examples

```bash
curl -i http://localhost:8080/eureka/apps #all apps  
curl -i http://localhost:8080/eureka/apps/estuary #all apps containing estuary  
curl -i http://localhost:8080/eureka/apps/your_app_name #all apps designated by your app name  
 ```

## Compilation - pyinstaller

```shell
python -m PyInstaller --onefile --clean --add-data="rest/api/templates/:rest/api/templates/" main.py
```

```cmd
python -m PyInstaller --onefile --clean --add-data="rest/api/templates/;rest/api/templates/" main.py
```

## Use cases

- Input for Estuary UI: commands / file transfers / service infrastructure registered in Eureka
- L7 HTTP messages to the Agents (environment set / commands / file upload & download)
- Listings of Apps registered with Eureka.

## Service run

### Docker compose

    docker-compose up

### Eureka registration

Estuary discovery will boot, and it will connect to the Eureka. Then it will be able to list all apps.

Start Eureka server with docker:

```bash
docker run -p 8080:8080 estuaryoss/netflix-eureka:1.9.25
```

Start your container by specifying the eureka server in order to discover all other apps.  
Optionally you can set PORT environment variable (default=8080).

    docker run \
    -e EUREKA_SERVER=http://10.10.15.30:8080/eureka/v2
    -e APP_IP=10.10.15.25
    -e PORT=8081
    -p 8081:8080
    estuaryoss/discovery:<tag>

### Kubernetes

    kubectl apply -f k8sdeployment.yml

### Fluentd logging

Please consult [Fluentd](https://github.com/fluent/fluentd) for logging setup.  
Estuary-discovery tags all logs in format ```estuary-discovery.**```

Matcher example:

```xml

<match estuary*.**>
        @type stdout
        </match>
```

Run example:

    docker run \
    -e FLUENTD_IP_PORT=10.10.15.28:24224
    -p 8080:8080
    estuaryoss/discovery:<tag>

### Authentication

For auth set HTTP_AUTH_USER & HTTP_AUTH_PASSWORD env variables.

[!!!]() Use these env variables to secure the service. [!!!]()

Run example:

```shell script
docker run \
-e HTTP_AUTH_USER=admin \
-e HTTP_AUTH_PASSWORD=estuaryoss123! \
-p 8080:8080
estuaryoss/discovery:<tag>
```

Then, access the Http Api. Call example:

```shell script
curl -i -u admin:estuaryoss123! http:localhost:8080/about
```  

Because discovery acts as a stack aggregator hitting agents, you must use the same HTTP_AUTH_USER &
HTTP_AUTH_PASSWORD   
across all stack, otherwise the aggregation won't work, because the headers are forwarded as they are sent.

### Enable HTTPS

Set **HTTPS_ENABLE** env var option to *true* or *false*.    
Set the certificate and the private key path with **HTTPS_CERT** and **HTTPS_KEY** env variables. If you do not set cert
and private key file env vars, it defaults to a folder in the same path called *https*, and the default files *
https/cert.pem* and *https/key.pem*.

## Environment variables injection

User defined environment variables will be stored in a 'virtual' environment. The extra env vars will be used by the
process that executes system commands.  
There are two ways to inject user defined environment variables.

- call POST on **/env** endpoint. The body will contain the env vars in JSON format. E.g. {"FOO1":"BAR1"}
- create an **environment.properties** file with the extra env vars needed and place it in the same path as the JAR.
  Example in this repo.

*! All environment variables described above can also be set using **environment.properties**.*

### Output example

curl -i http://172.17.0.22:8081/eureka/apps

```json
{
  "code": 1000,
  "message": "Success",
  "description": {
    "estuary-discovery": [
      {
        "ipAddr": "localhost",
        "port": "8081",
        "securePort": "8081",
        "app": "estuary-discovery",
        "metadata": {
          "management.port": "8081"
        },
        "homePageUrl": "http://localhost:8081/",
        "healthCheckUrl": "http://localhost:8081/ping",
        "statusPageUrl": "http://localhost:8081/ping"
      }
    ],
    "estuary-agent-java": [
      {
        "ipAddr": "192.168.0.41",
        "port": "8082",
        "securePort": "443",
        "app": "estuary-agent-java",
        "metadata": {
          "name": "Estuary-Agent",
          "management.port": "8082"
        },
        "homePageUrl": "http://localhost:8082/",
        "healthCheckUrl": "http://localhost:8082/actuator/health",
        "statusPageUrl": "http://localhost:8082/actuator/info"
      }
    ]
  },
  "path": "/eureka/apps?",
  "timestamp": "2021-12-19 12:03:51.375734",
  "name": "Estuary-Discovery",
  "version": "4.2.4"
}
```

Support
project: <a href="https://paypal.me/catalindinuta?locale.x=en_US"><img src="https://lh3.googleusercontent.com/Y2_nyEd0zJftXnlhQrWoweEvAy4RzbpDah_65JGQDKo9zCcBxHVpajYgXWFZcXdKS_o=s180-rw" height="40" width="40" align="center"></a>

## Estuary stack

[Estuary agent](https://github.com/estuaryoss/estuary-agent)  
[Estuary discovery](https://github.com/estuaryoss/estuary-discovery)  
[Estuary UI](https://github.com/estuaryoss/estuary-ui)   
