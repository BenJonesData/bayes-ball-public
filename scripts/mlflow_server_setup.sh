#!/bin/bash

nohup mlflow server --backend-store-uri sqlite:///mlflow/mlflow.db \
    --default-artifact-root ./mlflow/mlruns \
    --host 0.0.0.0 --port 5001 > mlflow/mlflow.log 2>&1 &