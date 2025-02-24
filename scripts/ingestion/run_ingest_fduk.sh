#!/bin/bash

# This file is intended as a quick means of running ingest_fduk.py
# This file can be editted and ran using `bash scripts/ingestion/run_ingest_fduk.sh`
# Please do not push any changes to this file 

poetry run python scripts/ingestion/ingest_fduk.py \
    --start_year 0 \
    --end_year 25 \
    --leagues 'E0' 'I1' \
    --columns 'HomeTeam' 'AwayTeam' 'FTR' 'B365H' \
    --save_filename 'ingested_fduk_data' \
    --enrich True