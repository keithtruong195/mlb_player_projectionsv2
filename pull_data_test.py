import pybaseball as pb
import os
import polars as pl

print(pb.playerid_lookup("schmitt", "casey"))

print(pb.statcast_batter("2026-04-01", "2026-07-30", 669477))