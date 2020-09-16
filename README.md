<h1 align="center"><img src="./docs/images/banner_discovery.png" alt="Testing as a service"></h1>

Support project: <a href="https://paypal.me/catalindinuta?locale.x=en_US"><img src="https://lh3.googleusercontent.com/Y2_nyEd0zJftXnlhQrWoweEvAy4RzbpDah_65JGQDKo9zCcBxHVpajYgXWFZcXdKS_o=s180-rw" height="40" width="40" align="center"></a>   

## Estuary discovery
Estuary discovery service. Aggregator of the estuary-stack. 
-   Reads the apps/services registered in Eureka  
-   Reads the tests from estuary-agent(s) registered in Eureka  
-   Reads the deployments from estuary-deployer(s) registered in Eureka.  
-   Controls test sessions by unicasting/broadcasting L7 HTTP messages to the agents  

## Coverage & code quality
[![Coverage Status](https://coveralls.io/repos/github/estuaryoss/estuary-discovery/badge.svg?branch=master)](https://coveralls.io/github/estuaryoss/estuary-discovery?branch=master)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/fc69b90ee90546158876e5344d9c2af2)](https://www.codacy.com/gh/estuaryoss/estuary-discovery?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=estuaryoss/estuary-discovery&amp;utm_campaign=Badge_Grade)
[![Maintainability](https://api.codeclimate.com/v1/badges/c0894a0a9785a3fb7afc/maintainability)](https://codeclimate.com/github/estuaryoss/estuary-discovery/maintainability)

## Linux status
[![Build Status](https://travis-ci.com/estuaryoss/estuary-discovery.svg?token=UC9Z5nQSPmb5vK5QLpJh&branch=master)](https://travis-ci.com/estuaryoss/estuary-discovery)

## Windows status
[![CircleCI](https://circleci.com/gh/estuaryoss/estuary-discovery.svg?style=svg)](https://circleci.com/gh/estuaryoss/estuary-discovery)

## Docker Hub
[alpine](https://hub.docker.com/r/estuaryoss/discovery) ![](https://img.shields.io/docker/pulls/estuaryoss/discovery.svg)

## Api docs
[4.0.8](https://app.swaggerhub.com/apis/dinuta/estuary-discovery/4.0.8)

## Postman collection
[Collection](https://documenter.getpostman.com/view/2360061/SVmpY31g)

## Service HTTP GET examples
```bash
curl -i http://localhost:8080/eurekaapps #all apps  
curl -i http://localhost:8080/eurekaapps/estuary #all apps containing estuary  
curl -i http://localhost:8080/eurekaapps/your_app_name #all apps designated by your app name  
 ```

## Use cases
-   Estuary-viewer stats: deployments / tests / infrastructure registered in Eureka
-   L7 RESTApi broadcasts to the Agents: start test/ get test status / get test results  
-   Rapid listing of apps registered with Eureka.
-   Other integrations

## Service run

### Docker compose
    docker-compose up
    
### Eureka registration
Estuary discovery will boot and it will connect to the Eureka. Then it will be able to list all apps.

Start Eureka server with docker:
```bash
docker run -p 8080:8080 estuaryoss/netflix-eureka:1.9.25
```

Start your container by specifying the eureka server in order to discover all other apps.  
Optionally you can set PORT environment variable (default=8080).  

    docker run \
    -e EUREKA_SERVER=http://10.10.15.30:8080/eureka/v2
    -e APP_IP_PORT=10.10.15.25:8081
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
For auth set HTTP_AUTH_TOKEN env variable.  

Run example:
```shell script
docker run \
-e HTTP_AUTH_TOKEN=mysecret
-p 8080:8080
estuaryoss/discovery:<tag>
```
Then, access the Http Api. Call example:
```shell script
curl -i -H 'Token:mysecret' http:localhost:8080/about
```  
Because discovery acts as an stack aggregator hitting agents or deployers endpoints, you must use the same HTTP_AUTH_TOKEN 
across all stack, otherwise the aggregation won't work, because the headers are forwarded as they are sent.    

## Environment variables injection
User defined environment variables will be stored in a 'virtual' environment. The extra env vars will be used by the process that executes system commands.  
There are two ways to inject user defined environment variables.    
-   call POST on **/env** endpoint. The body will contain the env vars in JSON format. E.g. {"FOO1":"BAR1"}  
-   create an **environment.properties** file with the extra env vars needed and place it in the same path as the JAR. Example in this repo.  

*! All environment variables described above can also be set using **environment.properties**.*

### Output example
curl -i http://172.17.0.22:8081/eurekaapps
```json
{
   "code" : 1000,
   "description" : {
      "estuary-agent" : [
         {
            "app" : "estuary-agent",
            "healthCheckUrl" : "http://172.17.0.22:8082/ping",
            "homePageUrl" : "http://172.17.0.22:8082/",
            "ipAddr" : "172.17.0.22",
            "port" : "8082",
            "statusPageUrl" : "http://172.17.0.22:8082/ping"
         }
      ],
      "estuary-discovery" : [
         {
            "app" : "estuary-discovery",
            "healthCheckUrl" : "http://172.17.0.22:8081/ping",
            "homePageUrl" : "http://172.17.0.22:8081/",
            "ipAddr" : "172.17.0.22",
            "port" : "8081",
            "statusPageUrl" : "http://172.17.0.22:8081/ping"
         }
      ]
   },
   "message" : "Success",
   "name" : "estuary-discovery",
   "timestamp" : "2020-08-15 20:18:36.359046",
   "path" : "/eurekaapps?",
   "version" : "4.0.8"
}
```

## Estuary stack
[Estuary deployer](https://github.com/dinuta/estuary-deployer)  
[Estuary agent](https://github.com/dinuta/estuary-agent)  
[Estuary discovery](https://github.com/dinuta/estuary-discovery)  
[Estuary viewer](https://github.com/dinuta/estuary-viewer)  
