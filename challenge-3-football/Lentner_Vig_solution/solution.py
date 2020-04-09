import pandas as pd
import pickle

data = pickle.load(open("data.pkl", "rb"))
match_info_all = (
    data["match"]
    .merge(data["round"], how="left")
    .merge(data["season"], how="left")
    .merge(data["competition"], how="left")
    .merge(data["region"], how="left")
)
sub = data["sub"].rename(columns={"sub_id": "player_id"})
lineup = data["lineup"].rename(columns={"person_id": "player_id"})
onfield = pd.concat([sub, lineup], sort=True)
top5_teams = (
    data["event"]
    .rename(columns={"person_id": "player_id"})
    .merge(
        onfield[["match_id", "player_id", "side"]],
        how="inner",
        on=["match_id", "player_id"],
    )
)
top5_teams = pd.concat(
    [
        top5_teams.loc[top5_teams["side"] == "home"]
        .merge(data["match"][["match_id", "home_team"]], how="inner", on=["match_id"])
        .rename(columns={"home_team": "team"}),
        top5_teams.loc[top5_teams["side"] == "away"]
        .merge(data["match"][["match_id", "away_team"]], how="inner", on=["match_id"])
        .rename(columns={"away_team": "team"}),
    ]
)
top5_teams = pd.concat(
    [
        top5_teams.loc[top5_teams["side"] == "home"]
        .merge(data["match"][["match_id", "away_team"]], how="inner", on=["match_id"])
        .rename(columns={"away_team": "team_a"}),
        top5_teams.loc[top5_teams["side"] == "away"]
        .merge(data["match"][["match_id", "home_team"]], how="inner", on=["match_id"])
        .rename(columns={"home_team": "team_a"}),
    ]
)


def get_top_n(df, group, sort, n):
    out = (
        df.groupby(group)
        .count()
        .sort_values(by=[sort], ascending=False)
        .iloc[0:n]
        .reset_index()
    )
    out["player_id"] = [int(i) for i in out["player_id"]]
    return out


def top_player(df):
    top = pd.merge(
        df,
        data["player"][["First name", "Last name", "player_id"]],
        how="inner",
        on="player_id",
    )
    return top


# 1.
data["goal"]["goal_id"] = [i for i in range(data["goal"].shape[0])]
g_match = pd.merge(
    data["goal"], match_info_all[["match_id", "region_id", "season_id"]], how="left"
)
goal_n = g_match.groupby("scorer_id")["goal_id"].nunique().loc[lambda x: x >= 20]
region_n = g_match.groupby("scorer_id")["region_id"].nunique().loc[lambda x: x >= 4]
# 2.
suspended = data["sidelined"].loc[data["sidelined"]["reason"] == "Suspended"]
susp = pd.merge(suspended, data["match_inf"][["match_id", "referee_id"]], how="left")
grouped = susp.groupby(["player_id", "referee_id"]).count()
# 3.

# 4.
left = data["player"][["Foot", "player_id"]].loc[data["player"]["Foot"] == "Left"]
merged = onfield.merge(left, how="left", on="player_id")
# 5.
result = pd.merge(sub, suspended, how="inner", on=["match_id", "player_id"])
# 6.
missed = top5_teams.loc[top5_teams["event"] == "penalty-miss"]
grouped_pen = missed.groupby(["match_id"]).count()
# TOP5
# 1.
ip = g_match.dropna(subset=["assister_id"]).rename(columns={"assister_id": "player_id"})
topassists = get_top_n(ip, ["player_id", "season_id"], "goal_id", 6,)
# 2.
sub["sub"] = 1
g_match_2 = pd.merge(data["goal"], match_info_all["match_id"], how="left")
subbed_goals = pd.merge(
    g_match_2.rename(columns={"scorer_id": "player_id"}),
    sub[["match_id", "player_id", "sub"]],
    how="inner",
    on=["player_id", "match_id"],
).drop_duplicates()
top_subbed_goals = get_top_n(subbed_goals, "player_id", "goal_id", 5)
# 3.
top_sat = get_top_n(sub[sub["time"].isnull()], "player_id", "sub", 5)
# 4.
ind = data["goal"].loc[data["goal"]["minute"] == "'"].index[0]
data["goal"].at[ind, "minute"] = "0'"
data["goal"]["first half"] = [int(i.split("'")[0]) for i in data["goal"]["minute"]]
first_half = data["goal"].loc[data["goal"]["first half"] <= 45]
first_half = first_half.rename(columns={"scorer_id": "player_id"})
top_first = get_top_n(first_half, "player_id", "minute", 5)
# 5.
sort_reason = data["sidelined"].groupby(["player_id", "reason"]).count().reset_index()
top_reason = get_top_n(sort_reason, "player_id", "reason", 5)
# 6.
work = data["goal"][["match_id", "scorer_id", "assister_id"]]
work = work.rename(columns={"scorer_id": "player_id"})
top_sa = get_top_n(work, ["player_id", "match_id"], "assister_id", 5)

# Features
last_21_day = match_info_all.sort_values(["start_time"], ascending=False)
last_21_day["last_days"] = last_21_day.apply(
    lambda x: (last_21_day.iloc[0, 5].date() - x["start_time"].date()), axis=1
)
a = last_21_day[last_21_day["last_days"] < "22 Days"]
a["Team"] = a["home_team"]
b = a.copy()
b["Team"] = b["away_team"]
last_21_day_small = pd.concat([a, b])
# 1
groupby_1 = last_21_day_small.groupby(["Team"]).count()

last_21_day = pd.merge(
    last_21_day, groupby_1["score"], left_on="home_team", right_index=True, how="outer"
)
last_21_day = pd.merge(
    last_21_day,
    groupby_1["round_id"],
    left_on="away_team",
    right_index=True,
    how="outer",
)
last_21_day.rename(columns={"score_y": "home_team_matches"}, inplace=True)
last_21_day.rename(columns={"round_id_y": "away_team_matches"}, inplace=True)
# 2
groupby_2 = last_21_day_small[["Team", "comp_id"]].groupby(["Team"]).nunique()
last_21_day = pd.merge(
    last_21_day, groupby_2["Team"], left_on="home_team", right_index=True, how="outer"
)
last_21_day = pd.merge(
    last_21_day,
    groupby_2["comp_id"],
    left_on="away_team",
    right_index=True,
    how="outer",
)
last_21_day.rename(columns={"Team": "home_team_competition"}, inplace=True)
last_21_day.rename(columns={"comp_id_y": "away_team_competition"}, inplace=True)
# 3
data["sidelined"]["new_key"] = data["sidelined"].apply(
    lambda x: (str(x["match_id"]) + str(x["player_id"])), axis=1
)
data["goal"]["new_key"] = data["goal"].apply(
    lambda x: (str(x["match_id"]) + str(x["scorer_id"])), axis=1
)

groupby_3 = data["goal"][["score", "new_key"]].groupby(["new_key"]).count()

data["sidelined"] = pd.merge(
    data["sidelined"], groupby_3, left_on="new_key", right_index=True, how="left"
)
sidelined_df_h = data["sidelined"][data["sidelined"]["side"] == "home"]
sidelined_df_a = data["sidelined"][data["sidelined"]["side"] == "away"]

groupby_3_home = sidelined_df_h[["match_id", "score"]].groupby(["match_id"]).count()
groupby_3_away = sidelined_df_a[["match_id", "score"]].groupby(["match_id"]).count()

last_21_day_small = pd.merge(
    last_21_day_small, groupby_3_home, left_on="match_id", right_index=True, how="left"
)
last_21_day_small = pd.merge(
    last_21_day_small, groupby_3_away, left_on="match_id", right_index=True, how="left"
)
last_21_day_small.rename(
    columns={"score_x": "home_team_scores", "score_y": "away_team_scores"}, inplace=True
)

last_21_day_small = last_21_day_small.drop_duplicates(subset=["match_id"])
last_21_day = pd.merge(
    last_21_day,
    last_21_day_small[["match_id", "home_team_scores", "away_team_scores"]],
    on="match_id",
    how="left",
)

# 4
d = last_21_day.copy()
d["Team"] = d["home_team"]
e = d.copy()
e["Team"] = e["away_team"]
last_21_day_big = pd.concat([e, d]).sort_values(["start_time"], ascending=False)

groupby_5 = last_21_day_big[["Team", "last_days"]].groupby(["Team"]).min()

last_21_day = pd.merge(
    last_21_day, groupby_5, left_on="home_team", right_index=True, how="left"
)
last_21_day.rename(columns={"last_days_y": "home_team_last_match"}, inplace=True)

last_21_day = pd.merge(
    last_21_day, groupby_5, left_on="away_team", right_index=True, how="left"
)
last_21_day.rename(columns={"last_days": "away_team_last_match"}, inplace=True)

# 9
lineup_df = pd.merge(
    data["lineup"],
    data["player"][["player_id", "Nationality"]],
    left_on=["person_id"],
    right_on=["player_id"],
    how="left",
)
groupby_6_home = (
    lineup_df[lineup_df["side"] == "home"][["match_id", "Nationality"]]
    .groupby(["match_id"])
    .nunique()
)
groupby_6_away = (
    lineup_df[lineup_df["side"] == "away"][["match_id", "Nationality"]]
    .groupby(["match_id"])
    .nunique()
)
last_21_day = pd.merge(
    last_21_day, groupby_6_home, left_on="match_id", right_index=True, how="outer"
)
last_21_day = pd.merge(
    last_21_day, groupby_6_away, left_on="match_id", right_index=True, how="outer"
)
last_21_day.rename(
    columns={"Nationality_x": "nationality_home", "Nationality_y": "nationality_away"},
    inplace=True,
)
last_21_day = last_21_day.drop(["match_id_y"], axis=1)
