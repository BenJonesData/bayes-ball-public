import pandas as pd
from typing import List
from loguru import logger
import os
from src.helper_functions import get_train_test


def create_dataframe(
    data: pd.DataFrame, exclude_seasons: List[str] = None
) -> pd.DataFrame:

    data = data.copy()
    logger.info("Starting dataset creation")

    if exclude_seasons is not None:
        data = data[~data["season"].isin(exclude_seasons)]
        logger.info(f"Sucessfully removed seasons: {exclude_seasons}")

    home_h1_data = data.loc[
        data["season_half_h"] == 1,
        [
            "season",
            "div",
            "hometeam",
            "fthg",
            "hthg",
            "hs",
            "hst",
            "hc",
            "hf",
            "hy",
            "hr",
            "ftag",
            "htag",
            "as",
            "ast",
            "ac",
            "af",
            "ay",
            "ar",
        ],
    ]
    away_h1_data = data.loc[
        data["season_half_a"] == 1,
        [
            "season",
            "div",
            "awayteam",
            "ftag",
            "htag",
            "as",
            "ast",
            "ac",
            "af",
            "ay",
            "ar",
            "fthg",
            "hthg",
            "hs",
            "hst",
            "hc",
            "hf",
            "hy",
            "hr",
        ],
    ]

    home_h1_data.rename(
        columns={
            "hometeam": "team",
            "fthg": "avg_goals_scored",
            "hthg": "avg_ht_goals_scored",
            "hs": "avg_shots",
            "hst": "avg_sot",
            "hc": "avg_corners",
            "hf": "avg_fouls",
            "hy": "avg_yellows",
            "hr": "avg_reds",
            "ftag": "avg_goals_conceded",
            "htag": "avg_ht_goals_conceded",
            "as": "avg_shots_faced",
            "ast": "avg_sot_faced",
            "ac": "avg_corners_faced",
            "af": "avg_fouls_against",
            "ay": "avg_yellows_against",
            "ar": "avg_reds_against",
        },
        inplace=True,
    )

    away_h1_data.rename(
        columns={
            "awayteam": "team",
            "ftag": "avg_goals_scored",
            "htag": "avg_ht_goals_scored",
            "as": "avg_shots",
            "ast": "avg_sot",
            "ac": "avg_corners",
            "af": "avg_fouls",
            "ay": "avg_yellows",
            "ar": "avg_reds",
            "fthg": "avg_goals_conceded",
            "hthg": "avg_ht_goals_conceded",
            "hs": "avg_shots_faced",
            "hst": "avg_sot_faced",
            "hc": "avg_corners_faced",
            "hf": "avg_fouls_against",
            "hy": "avg_yellows_against",
            "hr": "avg_reds_against",
        },
        inplace=True,
    )
    logger.info("Home and away dataframes created succesfully")

    all_h1_data = pd.concat([home_h1_data, away_h1_data])
    stats_h1 = (
        all_h1_data.groupby(["season", "div", "team"]).mean().reset_index()
    )
    logger.info("Home and away dataframes succesfully combined and grouped")

    results_h2 = data.loc[
        (data["season_half_h"] == 2) & (data["season_half_a"] == 2),
        [
            "season",
            "div",
            "date",
            "hometeam",
            "awayteam",
            "ftr",
            "b365h",
            "b365d",
            "b365a",
        ],
    ]
    results_h2.rename(
        columns={"hometeam": "h_team", "awayteam": "a_team"}, inplace=True
    )

    results_h2 = results_h2.merge(
        stats_h1.add_prefix("h_"),
        left_on=["season", "div", "h_team"],
        right_on=["h_season", "h_div", "h_team"],
        how="inner",
    )
    results_h2 = results_h2.merge(
        stats_h1.add_prefix("a_"),
        left_on=["season", "div", "a_team"],
        right_on=["a_season", "a_div", "a_team"],
        how="inner",
    )
    logger.info("Team stats succesfully merged onto game data")

    results_h2.drop(
        columns=["h_season", "h_div", "a_season", "a_div"], inplace=True
    )
    logger.info("Duplicate columns successfully dropped")

    results_h2["h_win"] = (results_h2["ftr"] == "H").astype(int)

    results_h2.dropna(subset="b365h", inplace=True)
    results_h2 = results_h2[results_h2["b365h"] != 0]

    bookies_margin = (
        (1 / results_h2["b365h"])
        + (1 / results_h2["b365d"])
        + (1 / results_h2["b365a"])
    )
    results_h2["bookies_prob"] = bookies_margin / results_h2["b365h"]

    logger.info("Dataset creation complete")
    logger.info(f"Dataset length: {len(results_h2)}")

    return results_h2


if __name__ == "__main__":
    raw_games = pd.read_csv("data/raw_games.csv")
    df = create_dataframe(
        raw_games, exclude_seasons=["19_20", "20_21", "24_25"]
    )

    train_val, test = get_train_test(df, test_size=3, random_state=147)

    train_val = train_val.drop(
        columns=[
            "div",
            "date",
            "h_team",
            "a_team",
            "ftr",
            "b365h",
            "b365d",
            "b365a",
        ]
    )

    train_val.to_csv("data/train_val_data.csv", index=False)
    test.to_csv("data/test_data.csv", index=False)

    os.remove("data/raw_games.csv")
