# File to merge
import pandas as pd
import os

if __name__=='__main__':
    fix = pd.read_csv('data/fixtures.csv')
    stats = pd.read_csv("data/statistics.csv")

    df_home_team = stats.groupby('fixture_id').first().reset_index()
    df_away_team = stats.groupby('fixture_id').last().reset_index()

    df_home_team.drop(columns = ['team_id', 'team_name'], inplace=True)
    df_away_team.drop(columns = ['team_id', 'team_name'], inplace=True)

    df_home_team = df_home_team.rename(columns={col: f"home_{col}" for col in df_home_team.columns if col != "fixture_id"})
    df_away_team = df_away_team.rename(columns={col: f"away_{col}" for col in df_away_team.columns if col != "fixture_id"})
    df_all_stats = df_home_team.merge(df_away_team, on=['fixture_id'])

    df = fix.merge(df_all_stats, on=['fixture_id'])
    os.makedirs("data/", exist_ok=True)
    df.to_csv("data/fixtures_statistics.csv", index=False)