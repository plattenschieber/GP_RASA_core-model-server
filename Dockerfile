FROM python:3.6-alpine
COPY start-model-server.py server/
WORKDIR server/

EXPOSE 8000

ENTRYPOINT exec sh -c "python start-model-server.py"