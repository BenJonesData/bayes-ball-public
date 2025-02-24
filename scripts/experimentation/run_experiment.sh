#!/bin/bash

# This file is intended as a quick means of running run_experiment.py
# This file can be editted and ran using `bash scripts/experimentation/run_experiment.sh`
# Please do not push any changes to this file 

poetry run python scripts/experimentation/experiment.py \
    --training_data_path 'data/train_val_data.csv' \
    --learning_rate 0.001 \
    --num_epochs 10000 \
    --num_samples 1000 \
    --num_batches 1 \
    --league_tag 'epl' \
    --hidden_units 8