import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from geopy.distance import geodesic

def calculate_distance(row):
    if row.name == 0:
        return 0
    prev_row = data.iloc[row.name - 1]
    return geodesic((prev_row['LAT'], prev_row['LON']), (row['LAT'], row['LON'])).km

# load JSON data
data = pd.read_json('filtered_data.json')
data['BaseDateTime'] = pd.to_datetime(data['BaseDateTime'])
data = data.sort_values(by='BaseDateTime')
data['TimeElapsed'] = (data['BaseDateTime'] - data['BaseDateTime'].min()).dt.total_seconds() / 3600.0

data['Distance'] = data.apply(calculate_distance, axis=1)
data['Total Distance'] = data['Distance'].cumsum()

# prepare data for linear regression models
time_passed = data['TimeElapsed'].values.reshape(-1, 1)
lat = data['LAT'].values
lon = data['LON'].values
lat_model = LinearRegression().fit(time_passed, lat)
lon_model = LinearRegression().fit(time_passed, lon)

future_times = np.array([data['TimeElapsed'].max() + i for i in range(1, 25)]).reshape(-1, 1)
predicted_lats = lat_model.predict(future_times)
predicted_lons = lon_model.predict(future_times)

predictions = pd.DataFrame({'Hours Ahead': range(1, 25),'Predicted LAT': predicted_lats,'Predicted LON': predicted_lons})

print(data[['BaseDateTime', 'LAT', 'LON', 'Distance', 'Total Distance']])