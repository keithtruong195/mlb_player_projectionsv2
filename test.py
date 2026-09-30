import pybaseball as pb
import os
import pandas as pd

try:
    data = pb.batting_stats_bref(2025)
    player_stats = data[data['Name'].str.contains('Casey Schmitt', case=False)]
    print(player_stats)
except Exception as e:
    print(f"Error: {e}")

print(pb.playerid_lookup('webb', 'logan'))

player1_data = pb.playerid_lookup('kershaw')
print(player1_data)

print(pb.statcast_pitcher_pitch_arsenal(2019,250))

print(pb.statcast_batter)


