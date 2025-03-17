import pandas as pd
import numpy as np

# load AIS data into pandas DataFrame
df = pd.read_csv("AIS_2024_01_01.csv")

# filter for moving vessels
# add a shifted column for the next latitude and longitude values
# and calculate abs diff between current and next LAT, LON
df = df[df['SOG'] > 0]
df['LAT_next'] = df['LAT'].shift(-1)
df['LON_next'] = df['LON'].shift(-1)
df['LAT_diff'] = np.abs(df['LAT'] - df['LAT_next'])
df['LON_diff'] = np.abs(df['LON'] - df['LON_next'])

# filter vessels where next LAT and LON differnece greater than 0.01 degree
# and drop columns
filtered_df = df[(df['LAT_diff'] > 0.01) & (df['LON_diff'] > 0.01)]
filtered_df = filtered_df.drop(columns=['LAT_next', 'LON_next', 'LAT_diff', 'LON_diff'])

print(filtered_df)
