<h1 align="center"><img src="./docs/images/banner_estuary.png" alt="Testing as a service with Docker"></h1>  

Please donate: <a href="https://paypal.me/catalindinuta?locale.x=en_US"><img src="https://pbs.twimg.com/profile_images/1145724063106519040/b1L98qh9_400x400.jpg" height="40" width="40" align="center"></a>    

# Testing as a Service
## Estuary discovery
Estuary discovery service. Aggregator of the estuary-stack.

1. Reads the estuary apps registered in Eureka: deployer, testrunner or discovery(itself)
2. Reads the deployments from estuary-testrunner(s) registered in Eureka
3. Reads the deployments from estuary-deployer(s) registered in Eureka

## Build & Coverage
[![Build Status](https://travis-ci.org/dinuta/estuary-discovery.svg?branch=master)](https://travis-ci.org/dinuta/estuary-discovery)
[![Coverage Status](https://coveralls.io/repos/github/dinuta/estuary-discovery/badge.svg?branch=master)](https://coveralls.io/github/dinuta/estuary-discovery?branch=master)

## Docker Hub
[![](https://images.microbadger.com/badges/image/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own image badge on microbadger.com")[![](https://images.microbadger.com/badges/version/dinutac/estuary-discovery.svg)](https://microbadger.com/images/dinutac/estuary-discovery "Get your own version badge on microbadger.com")![](https://img.shields.io/docker/pulls/dinutac/estuary-discovery.svg)

## Api docs
/api/docs

## Postman collection
https://documenter.getpostman.com/view/2360061/SVmpY31g


Use cases:
1. Useful for estuary-viewer frontend app.
2. Useful for rapid listing of estuary services in production/your environment.

## Service run
##### Using docker compose
    docker-compose up
    
##### Using docker run - eureka registration
Estuary discovery will boot and it will connect to the Eureka. Then it will be able to list all apps.

Start Eureka server with docker:

    docker run -p 8080:8080 netflixoss/eureka:1.3.1

Start your container by specifying the eureka server in order to discover all other apps:

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
    
 ##### Using kubernetes
     kubectl apply -f k8sdeployment.yml  
    
## Estuary stack
[Estuary deployer](https://github.com/dinuta/estuary-deployer)  
[Estuary testrunner](https://github.com/dinuta/estuary-testrunner)  
[Estuary discovery](https://github.com/dinuta/estuary-discovery)  
[Estuary viewer](https://github.com/dinuta/estuary-viewer)  
