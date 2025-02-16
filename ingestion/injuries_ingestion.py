import pandas as pd
import requests
from credentials import API_KEY, HEADERS
from config import all_leagues, seasons
import json
from tqdm import tqdm
import os

def get_injury_data(league_id, season):
    url = "https://v3.football.api-sports.io/injuries"

    params = {
        "league": league_id,
        "season": season
    }

    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()
    injuries = data.get("response", [])
    df = pd.json_normalize(injuries)
    df.columns = [col.replace('.', '_') for col in df.columns]
    return df

def get_all_injury_data():
    all_injuries_df = pd.DataFrame()
    for league_id in all_leagues:
        for season in seasons:
            df = get_injury_data(league_id, season)
            all_injuries_df = pd.concat([all_injuries_df, df], ignore_index=True)

    os.makedirs("data/", exist_ok=True)
    all_injuries_df.to_csv("data/injuries.csv", index=False)

if __name__=='__main__':
    get_all_injury_data()

