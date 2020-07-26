Production ready EFK stack.

Set on the linux machine where you run the docker compose, the following command: (You might set it again if you reboot the machine)
```bash
sysctl -w vm.max_map_count=262144
```

For Windows, search for the linux machine that runs containers or the HyperV VM.

Fluentd won't connect at the start to the ES cluster, because ES takes times to boot. Don't worry it will retry the connection.

All env should be up and running in ~1 minute.

## Boot up 
```bash
docker-compose up --build
```

## ElasticSearch 
http://localhost:9200  

## Kibana
http://localhost:5601

## Elastic APM
http://localhost:8200 
