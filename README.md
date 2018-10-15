# Model-Server for Core
A http server that takes models and save them to provide them requesting instances of rasa core.

## Structure
* *bamboo-spec* build pipeline configuration for bamboo
* *docker* all docker specific compose files
* *start-model-server.py* start script for the server

## Deploy and run the project
To deploy and run this project docker is mandatory, you would need to install docker as well as docker stack or docker compose.

### Build
You can run the build by the following command. We will tag the image with our docker registry url and the projects name.
```bash
docker build -t docker.nexus.gpchatbot.archi-lab.io/chatbot/core-model-server .
```

### Run
In order to run the server you will need to create a docker network which is called 'chatbot'. You can do this by running the following command:
```bash
docker network create chatbot
```
Then you can start the server with the given compose file
```bash
docker-compose -p gpb -f ./docker/docker-compose.yaml up
```

## Example requests
To get a model a request like this can be made:
```bash
GET http://localhost:8000/models/core
```
If the header "If-None-Match" is set with the current version a 204 No Content will be returned.
If the header does not match the current version a new model with content-type: application/zip will be returned.

To send the server a new model a post request can be made. If wanted a semantic version can be added with the "version" header
```bash
POST http://localhost:8000/models/core

HEADER (optional):
    Content-Type: application/zip
    version: X.X.X

CONTENT:
    .zip file
```

