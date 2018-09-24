#FROM python:3.6
FROM rasa/rasa_core:0.12.0a2

COPY . /model-server
WORKDIR /model-server
RUN apt-get update && apt-get install -y zip

EXPOSE 8000

ENTRYPOINT exec sh ./start-server.sh