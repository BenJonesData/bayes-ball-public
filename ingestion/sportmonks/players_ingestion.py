import calendar
import json
import os
import re
import time
from datetime import datetime

import pandas as pd
import requests
from loguru import logger

from ingestion.sportmonks.config import BASE_URL, HEADERS, SAVE_LOCATION
from ingestion.sportmonks.league_codes_ingestion import get_leagues


def get_all_players_populate():
    all_players = []
    page = 1

    while True:
        endpoint_url = (
            f"{BASE_URL}/players?filters=populate&page={page}&per_page=1000"
        )
        response = requests.get(endpoint_url, headers=HEADERS)

        if response.status_code == 200:
            players = response.json()
            players = players.get("data", [])

            if not players:
                break

            all_players.extend(players)

            logger.info(f"Page {page} retrieved with {len(players)}.")
            page += 1

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}all_players.json", "w") as f:
        json.dump(all_players, f)


def get_all_players_with_statistics():
    include = "country;city;nationality;transfers;pendingTransfers;teams;statistics;latest;position;detailedPosition;lineups;trophies;metadata "

    all_players = []
    page = 1

    while True:
        endpoint_url = endpoint_url = (
            f"{BASE_URL}/players?include={include}&page={page}&per_page=50"
        )
        response = requests.get(endpoint_url, headers=HEADERS)

        if response.status_code == 200:
            players = response.json()
            players = players.get("data", [])

            if not players:
                break

            all_players.extend(players)

            logger.info(f"Page {page} retrieved with {len(players)}.")
            page += 1

    os.makedirs(f"{SAVE_LOCATION}", exist_ok=True)
    with open(f"{SAVE_LOCATION}/all_players_with_stats.json", "w") as f:
        json.dump(all_players, f)


if __name__ == "__main__":
    get_all_players_with_statistics()
