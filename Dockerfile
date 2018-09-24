FROM rasa/rasa_core:0.12.0a2 as training
#Add training data to context
COPY . .
#install zip
RUN apt-get update \
    && apt-get install -y zip
#train dialog and zip it
RUN python ./src/train_dialog.py \
    && mkdir /output && cd ./models/dialogue \
    && zip -r /output/model.zip ./* && cd -

FROM python:3.6-alpine
COPY start-model-server.py server/
COPY --from=training /output ./server
WORKDIR server/

EXPOSE 8000

ENTRYPOINT exec python start-model-server.py