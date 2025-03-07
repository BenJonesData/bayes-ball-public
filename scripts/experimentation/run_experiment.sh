#!/bin/bash

# This file is intended as a quick means of running run_experiment.py
# This file can be editted and ran using `bash scripts/experimentation/run_experiment.sh`
# Please do not push any changes to this file 

poetry run python scripts/experimentation/experiment.py \
    --experiment_name 'general-experiment' \
    --run_id '123456' \
    --run_description 'enter description here' \
    --training_data_path 'data/train_data.csv' \
    --validation_data_path 'data/val_data.csv' \
    --hidden_units 8 8 \
    --learning_rate 0.001 \
    --num_epochs 10000 \
    --num_samples 1000 \
    --num_batches 1 \
    --league_tag 'epl' 