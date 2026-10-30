"""
pybaseball quick tutorial -- run top to bottom, or comment sections in/out.

Every pybaseball function returns a pandas DataFrame, so once data is pulled
it's all just pandas.
"""
import pybaseball as pb
import pandas as pd

# Cache results on disk so re-running doesn't re-download (big speedup for Statcast).
pb.cache.enable()

# Show more columns when printing.
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 200)


# ---------------------------------------------------------------------------
# 1. Season stats for every player (Baseball-Reference)
# ---------------------------------------------------------------------------
# One row per player for the season: G, PA, AB, H, HR, BB, SO, BA, OBP, SLG, OPS...
batting = pb.batting_stats_bref(2025)
pitching = pb.pitching_stats_bref(2025)

print(batting.shape)            # (rows, columns)
print(batting.columns.tolist()) # what stats you get
print(batting.head())

# Filter like any DataFrame: qualified-ish hitters, sorted by OPS.
regulars = batting[batting["PA"] >= 400].sort_values("OPS", ascending=False)
print(regulars[["Name", "Tm", "PA", "HR", "BA", "OBP", "SLG", "OPS"]].head(10))

# Look up one player by name.
print(batting[batting["Name"].str.contains("Casey Schmitt", case=False)])

# A date range instead of a whole season (e.g. one month).
june = pb.batting_stats_range("2025-06-01", "2025-06-30")
print(june.shape)


# ---------------------------------------------------------------------------
# 2. Player IDs -- each site uses its own ID, this table maps between them
# ---------------------------------------------------------------------------
# key_mlbam is what Statcast uses; key_bbref / key_fangraphs for those sites.
judge = pb.playerid_lookup("judge", "aaron")
print(judge)
judge_id = int(judge["key_mlbam"].iloc[0])   # 592450


# ---------------------------------------------------------------------------
# 3. Statcast leaderboards (season-level, from Baseball Savant)
# ---------------------------------------------------------------------------
# Expected stats: xBA, xSLG, xwOBA vs actual.
# Note: the minPA argument doesn't reliably filter, so filter yourself.
xstats = pb.statcast_batter_expected_stats(2025)
xstats = xstats[xstats["pa"] >= 200]
print(xstats.sort_values("est_woba", ascending=False).head(10))

# Exit velo / barrels.
barrels = pb.statcast_batter_exitvelo_barrels(2025, minBBE=100)
print(barrels.head())


# ---------------------------------------------------------------------------
# 4. Statcast pitch-by-pitch for one player (big: ~100+ columns per pitch)
# ---------------------------------------------------------------------------
judge_pitches = pb.statcast_batter("2025-06-01", "2025-06-30", judge_id)
print(judge_pitches.shape)
print(judge_pitches[["game_date", "pitch_type", "release_speed",
                     "events", "launch_speed", "launch_angle"]].dropna().head(10))
# pb.statcast_pitcher(start, end, player_id) works the same way for pitchers.
# pb.statcast(start, end) pulls EVERY pitch league-wide -- keep the range short.


# ---------------------------------------------------------------------------
# 5. Save to parquet (preview of the next step -- pyarrow is already installed)
# ---------------------------------------------------------------------------
# batting.to_parquet("data/batting_2025.parquet", index=False)
# df = pd.read_parquet("data/batting_2025.parquet")
