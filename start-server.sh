#!/usr/bin/env bash
ls ./src
python ./src/train_dialog.py
cd ./models/dialogue && zip -r ../../models_123456.zip ./* && cd -
python ./start-model-server.py