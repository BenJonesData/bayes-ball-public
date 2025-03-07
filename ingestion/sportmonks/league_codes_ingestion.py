import calendar
import json
import re
import time
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

from ingestion.sportmonks.config import BASE_URL, HEADERS, SAVE_LOCATION


def get_leagues():
    logger.info("Getting league lookup codes")

    include = "country"
    endpoint_url = f"{BASE_URL}/leagues?include={include}"

    response = requests.get(endpoint_url, headers=HEADERS)

    if response.status_code == 200:
        leagues = response.json()
    else:
        print("Failed to retrieve data. Status code:", response.status_code)

    leagues_df = pd.json_normalize(leagues["data"])

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    leagues_df.to_csv(f"{SAVE_LOCATION}/leagues_lookup.csv", index=False)
    logger.info("League lookup codes saved")


if __name__ == "__main__":
    get_leagues()
