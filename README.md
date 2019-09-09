<h1 align="center"><img src="./docs/images/banner_estuary.png" alt="Testing as a service with Docker"></h1>  

Please donate: <a href="https://paypal.me/catalindinuta?locale.x=en_US"><img src="https://pbs.twimg.com/profile_images/1145724063106519040/b1L98qh9_400x400.jpg" height="40" width="40" align="center"></a>    

# Testing as a Service with Docker
## estuary-discovery
Estuary discovery service. Reads the estuary apps from Eureka.

## Build & Coverage
[![Build Status](https://travis-ci.org/dinuta/estuary-discovery.svg?branch=master)](https://travis-ci.org/dinuta/estuary-discovery)
[![Coverage Status](https://coveralls.io/repos/github/dinuta/estuary-discovery/badge.svg?branch=master)](https://coveralls.io/github/dinuta/estuary-discovery?branch=master)
## Docker Hub
[![](https://images.microbadger.com/badges/image/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own image badge on microbadger.com")[![](https://images.microbadger.com/badges/version/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own version badge on microbadger.com")![](https://img.shields.io/docker/pulls/dinutac/estuary-discovery.svg)

## Api docs
https://app.swaggerhub.com/apis/dinuta/estuary-discovery/1.0.0

## Postman collection
https://documenter.getpostman.com/view/2360061/SVYrrdGe

## Container support
- mvn & java jdk  
- make  
- npm
- other: you can use this image as base and install on top your dependencies 

## TestRunner service usage
1. use the service embedded in this container and mount your testing framework
2. build your absolute custom framework image and integrate this service as a self-contained application service (cli). Read [doc](https://github.com/dinuta/estuary-discovery/wiki).

Use cases:
1. Useful for estuary-viewer frontend app.

## Service run
##### Using docker compose
    docker-compose up
    
##### Using docker run
    On Linux/Mac:

    docker run  
    -d 
    -p 8080:8080
    dinutac/estuary-discovery:<tag>
    
    On Windows:
            
    docker run 
    -d 
    -p 8080:8080
    dinutac/estuary-discovery:<tag>


##### Using docker run - eureka registration
To have all your testrunner instances in a central location we use netflix eureka. This means your client will discover
all services used for your test and then spread the tests across all.

Start Eureka server with docker:

    docker run -p 8080:8080 netflixoss/eureka:1.3.1

Start your containers by specifying the full hostname or ip of the host machine on where your testrunner service resides.

    On Linux/Mac:

    docker run \
    -e MAX_DEPLOY_MEMORY=80 \
    -e EUREKA_SERVER=http://10.10.15.25:8080/eureka/v2
    -e APP_IP_PORT=10.10.15.25:8081
    -p 8080:8080
    dinutac/estuary-discovery:<tag>

    On Windows:

    docker run \
    -e MAX_DEPLOY_MEMORY=80 \
    -e EUREKA_SERVER=http://10.10.15.25:8080/eureka/v2
    -e APP_IP_PORT=10.10.15.25:8081
    -p 8080:8080
    dinutac/estuary-discovery:<tag>
