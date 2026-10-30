"""
Advanced metrics (bat speed, barrel rate, etc.) for individual players.

Three ways to get them:
  A. Season leaderboards  -> one row per player, raw values (easiest)
  B. Percentile ranks     -> same metrics as 0-100 percentiles (the red/blue Savant bars)
  C. Pitch-by-pitch data  -> compute anything yourself, for any date range / split
"""
import io

import pandas as pd
import pybaseball as pb
import requests

pb.cache.enable()
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)

YEAR = 2025
PLAYER_ID = 592450  # Aaron Judge -- get others from pb.playerid_lookup("last", "first")


# ---------------------------------------------------------------------------
# A. Season leaderboards (raw values)
# ---------------------------------------------------------------------------
# Barrel rate, exit velo, hard-hit, launch angle.
barrels = pb.statcast_batter_exitvelo_barrels(YEAR, minBBE=1)
print(barrels[barrels["player_id"] == PLAYER_ID][
    ["last_name, first_name", "avg_hit_speed", "max_hit_speed", "ev95percent",
     "brl_percent", "brl_pa", "avg_hit_angle"]])

# Bat tracking (bat speed, swing length, blasts, squared-up) -- pybaseball has no
# function for this, but Baseball Savant serves the leaderboard as a CSV.
def savant_csv(url):
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return pd.read_csv(io.StringIO(r.content.decode("utf-8-sig")))

bat_tracking = savant_csv(
    "https://baseballsavant.mlb.com/leaderboard/bat-tracking"
    f"?seasonStart={YEAR}&seasonEnd={YEAR}&type=batter&minSwings=q&csv=true"
)
print(bat_tracking[bat_tracking["id"] == PLAYER_ID][
    ["name", "avg_bat_speed", "swing_length", "hard_swing_rate",
     "squared_up_per_swing", "blast_per_swing", "whiff_per_swing"]])

# Swing path: attack angle, attack direction, swing tilt.
swing_path = savant_csv(
    "https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle"
    f"?gameType=Regular&minSwings=q&seasonStart={YEAR}&seasonEnd={YEAR}&type=batter&csv=true"
)
print(swing_path[swing_path["id"] == PLAYER_ID][
    ["name", "avg_bat_speed", "attack_angle", "attack_direction",
     "swing_tilt", "ideal_attack_angle_rate"]])


# ---------------------------------------------------------------------------
# B. Percentile ranks (0-100, not raw values)
# ---------------------------------------------------------------------------
# Batters: xwoba, brl_percent, exit_velocity, hard_hit_percent, chase_percent,
#          whiff_percent, sprint_speed, bat_speed, squared_up_rate, ...
pct = pb.statcast_batter_percentile_ranks(YEAR)
print(pct[pct["player_id"] == PLAYER_ID].T)
# Pitchers: pb.statcast_pitcher_percentile_ranks(YEAR) -- adds xera, fb_velocity, fb_spin...


# ---------------------------------------------------------------------------
# C. Compute it yourself from pitch-by-pitch data
# ---------------------------------------------------------------------------
pitches = pb.statcast_batter(f"{YEAR}-03-01", f"{YEAR}-11-30", PLAYER_ID)

# Bat speed: only recorded on swings. Savant's average uses "competitive" swings
# (drops bunts, checked swings and very weak swings), so the raw mean runs a bit low.
swings = pitches.dropna(subset=["bat_speed"])
print("swings:", len(swings))
print("avg bat speed (all swings):", round(swings["bat_speed"].mean(), 1))
print("avg bat speed (fastest 90%):",
      round(swings[swings["bat_speed"] >= swings["bat_speed"].quantile(0.10)]["bat_speed"].mean(), 1))

# Barrel rate: Statcast marks barrels as launch_speed_angle == 6.
batted = pitches.dropna(subset=["launch_speed"])
batted = batted[batted["type"] == "X"]   # balls put in play
print("barrel % (per batted ball):", round((batted["launch_speed_angle"] == 6).mean() * 100, 1))

# This is where the pitch-level data shines: splits. For example, by pitch type:
print(swings.groupby("pitch_type")["bat_speed"].agg(["count", "mean"]).round(1))
