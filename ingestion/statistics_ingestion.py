import pandas as pd
import requests
from credentials import API_KEY, HEADERS
from config import all_leagues, seasons
import json
from tqdm import tqdm
import os

def get_fixture_ids():
    ids = pd.read_csv("data/ids/fixture_ids.csv")
    return ids

def get_statistics(fixture_id):
    BASE_URL = "https://v3.football.api-sports.io"

    url = f"{BASE_URL}/fixtures/statistics?fixture={fixture_id}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    fixtures = data.get("response", [])

    if not fixtures or all("statistics" not in f or not f["statistics"] for f in fixtures):
        df = pd.DataFrame()  # Empty DataFrame
    else:
        df = pd.json_normalize(fixtures)
        df.columns = [col.replace('.', '_') for col in df.columns]
        df = df.explode("statistics")
        df_stats = pd.json_normalize(df["statistics"])
        df = df.drop(columns=["statistics"]).reset_index(drop=True)
        df = pd.concat([df, df_stats], axis=1)
        df = df.pivot(index=["team_id", "team_name"], columns="type", values="value").reset_index()
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        df['fixture_id'] = fixture_id
    return df

def get_all_statistics():
    all_statistcs = pd.DataFrame()

    fixture_ids = get_fixture_ids()
    for fixture_id in tqdm(fixture_ids['fixture_ids']):
        df = get_fixture_statistics(fixture_id)
        all_statistcs = pd.concat([all_statistcs, df], ignore_index=True)
    
    os.makedirs("data/", exist_ok=True)
    all_statistcs.to_csv("data/statistics.csv", index=False)

if __name__=='__main__':
    get_all_fixture_statistics()