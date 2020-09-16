# Use cases

## Eureka client discovery

By starting discovery service poiting to the eureka server, the service will discover all the applications registred in eureka. The response given makes things easy to parse, and have a complete overview about the service infrastructure, live.

Based on app names, the user can make decisions.   
For example, the estuary deployer service can be registred with labels which results in different app names in eureka:

Decision examples:
- estuary-deployer_lab:8080 (lab machine can be provisioned with 4GB of ram, meaning that only 1 complete docker-compose env can be deployed)
- estuary-deployer_big:8080 (big machines can have 8GB of ram and therefore 2 envs can be deployed)

![image](https://user-images.githubusercontent.com/43060213/75604246-59432180-5adf-11ea-9854-219fb8a48f32.png)


## Unicast messages to the estuary-agents under same eureka server
Estuary discovery can send targeted http messages to the test-runners registered under the same eureka server / cluster of servers.   
In the testing as a service context this is used for test spreading.    

Unicast http request spec:  
**Headers**:  
IpAddr-Port: ip:port (of the targeted test runner)  
**Body**:  
Your suite start command  
E.g. mvn install -Dtype=IntegrationTests  
**Uri**:  
/agents/test/1   
**Method**:  
POST

## Broadcast messages to the estuary-agents under same eureka server
Estuary discovery can send broadcast http message(same message) to the test-runners registered under the same eureka server / cluster of servers.   
In the testing as a service context this is used for:
- hard reproducible bugs, where bug happens once at dozens/hundreds of tries.  
- determine rate of success
- determine the stability of the tests

Broadcast http request spec:   
**Body**:  
Your suite start command  
E.g. mvn install -Dtype=IntegrationTests  
**Uri**:  
/agents/commanddetached/1   
**Method**:  
POST

## Control test sessions in Kubernetes
If you choose to implement your testing as a service model in Kubernetes then discovery controls test session in through ingress.  
An example is [here](https://github.com/dinuta/estuary-viewer/blob/master/k8singress.yml) for estuary-viewer.

## Estuary-Viewer ingress in Kubernetes
Estuary viewer can spot the the test sessions and the stats of the estuary-stack in Kubernetes through k8s ingress.