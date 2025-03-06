import pandas as pd
from typing import Iterable, List
from loguru import logger
from collections import Counter
import json

from src.helper_functions import find_repo_root


def _enrich_data_fduk(data: pd.DataFrame) -> pd.DataFrame:
    output_data = data.copy()

    teams = list(output_data["home_team"].drop_duplicates())
    half_way_point = len(teams) - 1

    team_counter = Counter()
    game_num_h = []
    game_num_a = []
    for _, row in output_data.iterrows():
        team_counter[row["home_team"]] += 1
        game_num_h.append(team_counter[row["home_team"]])
        team_counter[row["away_team"]] += 1
        game_num_a.append(team_counter[row["away_team"]])
    output_data["game_num_h"] = game_num_h
    output_data["game_num_a"] = game_num_a

    output_data["season_half_h"] = 1
    output_data["season_half_a"] = 1
    output_data.loc[
        output_data["game_num_h"] > half_way_point, "season_half_h"
    ] = 2
    output_data.loc[
        output_data["game_num_a"] > half_way_point, "season_half_a"
    ] = 2

    return output_data


def get_data_fduk(
    seasons: Iterable[int],
    leagues: List[str],
    columns: List[str] | None = None,
    enrich: bool = False,
) -> None:
    
    repo_root = find_repo_root()
    config_path = repo_root / "config" / "config.json"
    with open(config_path, "r") as f:
        column_mapping = json.load(f)
    
    if columns is None:
        columns = ["season"] + list(column_mapping.values())

    data_list = []
    for start_y in seasons:
        start_y_str = ("0" + str(start_y))[-2:]
        end_y_str = ("0" + str(start_y + 1))[-2:]
        season = start_y_str + end_y_str
        season_tag = start_y_str + "_" + end_y_str

        for league in leagues:
            url = (
                "https://www.football-data.co.uk/mmz4281/"
                + f"{season}/{league}.csv"
            )
            try:
                data = pd.read_csv(url)
                data=data.rename(columns=column_mapping)
                data["season"] = season_tag

                include_columns = [
                    col for col in columns if col in data.columns
                ]

                data = data[include_columns]

                if enrich:
                    data = _enrich_data_fduk(data)

                data_list.append(data)

                logger.info(
                    f"Sucessfully loaded data for {league} in {season_tag}"
                )
            except Exception as e:
                logger.info(
                    f"Error loading data for {league} in {season_tag}: {e}"
                )
                continue

    data_full = pd.concat(data_list).reset_index()

    reorder_columns = [col for col in columns if col in data_full.columns] + ["game_num_h", "game_num_a", "season_half_h", "season_half_a"]
    data_full = data_full[reorder_columns]

    return data_full
