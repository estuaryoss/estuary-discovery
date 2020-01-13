<h1 align="center"><img src="./docs/images/banner_estuary.png" alt="Testing as a service"></h1>

Support project: <a href="https://paypal.me/catalindinuta?locale.x=en_US"><img src="https://pbs.twimg.com/profile_images/1145724063106519040/b1L98qh9_400x400.jpg" height="40" width="40" align="center"></a>    

# Testing as a Service
## Estuary discovery
Estuary discovery service. Aggregator of the estuary-stack.

1.  Reads the estuary apps registered in Eureka: deployer, testrunner or discovery(itself), or others
2.  Reads the tests from estuary-testrunner(s) registered in Eureka
3.  Reads the deployments from estuary-deployer(s) registered in Eureka.

## Build & Coverage
[![Build Status](https://travis-ci.org/dinuta/estuary-discovery.svg?branch=master)](https://travis-ci.org/dinuta/estuary-discovery)
[![Coverage Status](https://coveralls.io/repos/github/dinuta/estuary-discovery/badge.svg?branch=master)](https://coveralls.io/github/dinuta/estuary-discovery?branch=master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/30ef547718d54f7485e57a5da936c557)](https://www.codacy.com/manual/dinuta/estuary-discovery?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dinuta/estuary-discovery&amp;utm_campaign=Badge_Grade)
## Docker Hub
[![](https://images.microbadger.com/badges/image/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own image badge on microbadger.com")[![](https://images.microbadger.com/badges/version/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own version badge on microbadger.com")![](https://img.shields.io/docker/pulls/dinutac/estuary-discovery.svg)

## Api docs
[Swagger](https://app.swaggerhub.com/apis/dinuta/estuary-discovery/4.0.1)

## Postman collection
[Collection](https://documenter.getpostman.com/view/2360061/SVmpY31g)

## Service HTTP GET examples
```bash
curl -i http://localhost:8080/eurekaapps #all apps  
curl -i http://localhost:8080/eurekaapps/estuary #all apps containing estuary  
curl -i http://localhost:8080/eurekaapps/your_app_name #all apps designated by your app name  
 ```

## Use cases
1.  Estuary-viewer stats: deployments / tests / infrastructure registered in Eureka
2.  L7 RESTApi broadcasts to the TestRunner services: start test/ get test status / get test results  
3.  Rapid listing of apps registered with Eureka.
4.  Integrations

## Service run

### Docker compose
    docker-compose up
    
### Eureka registration
Estuary discovery will boot and it will connect to the Eureka. Then it will be able to list all apps.

Start Eureka server with docker:

    docker run -p 8080:8080 netflixoss/eureka:1.3.1
    or
    docker run -p 8080:8080 dinutac/netflixoss-eureka:1.9.15

Start your container by specifying the eureka server in order to discover all other apps.  
Optionally you can set PORT environment variable (default=8080).  

    docker run \
    -e EUREKA_SERVER=http://10.10.15.25:8080/eureka/v2
    -e APP_IP_PORT=10.10.15.25:8081
    -p 8081:8080
    dinutac/estuary-discovery:<tag>
    
    Jinja2 templating can be done, just add:
    Windows:
    -v %cd%/inputs/templates:/data \ 
    -v %cd%/inputs/variables:/variables \
    
    Linux:
    -v $PWD/inputs/templates:/data \ 
    -v $PWD/inputs/variables:/variables \
    
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
    dinutac/estuary-discovery:<tag>

### Authentication
For auth set HTTP_AUTH_TOKEN env variable.  

Run example:
```shell script
docker run \
-e HTTP_AUTH_TOKEN=mysecret
-p 8080:8080
dinutac/estuary-discovery:<tag>
```
Then, access the Http Api. Call example:
```shell script
curl -i -H 'Token:mysecret' http:localhost:8080/about
```  
Because discovery acts as an stack aggregator hitting testrunner or deployers endpoints, you must use the same HTTP_AUTH_TOKEN 
across all stack, otherwise the aggregation won't work, because the headers are forwarded as they are sent.    
    
## Estuary stack
[Estuary deployer](https://github.com/dinuta/estuary-deployer)  
[Estuary testrunner](https://github.com/dinuta/estuary-testrunner)  
[Estuary discovery](https://github.com/dinuta/estuary-discovery)  
[Estuary viewer](https://github.com/dinuta/estuary-viewer)  
