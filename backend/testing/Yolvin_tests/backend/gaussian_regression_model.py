import numpy as np
import json
from datetime import datetime
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from sklearn.preprocessing import StandardScaler

# function to calculate time difference in hours
def calculate_time_diff(timestamp1, timestamp2):
    time1 = datetime.strptime(timestamp1, "%Y-%m-%dT%H:%M:%S")
    time2 = datetime.strptime(timestamp2, "%Y-%m-%dT%H:%M:%S")
    delta_time = (time2 - time1).total_seconds() / 3600 
    return delta_time

# function to calculate change in latitude and longitude
def calculate_position_change(lat1, lon1, lat2, lon2):
    # earth radius in km
    R = 6371.0

    lat1_rad, lon1_rad = np.radians(lat1), np.radians(lon1)
    lat2_rad, lon2_rad = np.radians(lat2), np.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = np.sin(dlat / 2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = R * c
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    return distance, delta_lat, delta_lon

# load JSON data
with open('filtered_data.json', 'r') as file:
    data = json.load(file)

filtered_data = [record for record in data if record['MMSI'] == 367067950]
X_train = []
y_train = []

for i in range(len(filtered_data) - 1):
    record1 = filtered_data[i]
    record2 = filtered_data[i + 1]
    
    delta_time = calculate_time_diff(record1['BaseDateTime'], record2['BaseDateTime'])
    distance, delta_lat, delta_lon = calculate_position_change(record1['LAT'], record1['LON'], record2['LAT'], record2['LON'])
    
    # x is features, y is the target
    X_train.append([record1['LAT'], record1['LON'], record1['SOG'], delta_time])
    y_train.append([delta_lat, delta_lon])

X_train = np.array(X_train)
y_train = np.array(y_train)

# adding features to model for training, need lat long sog delta_time from json data
lat_lon_features = X_train[:, :2]
other_features = X_train[:, 2:]  # SOG, delta_time, only ones being used right now, might need to add more tbh

# scale only using SOG and delta_time due to wanting ship data that moves
scaler = StandardScaler()
other_features_scaled = scaler.fit_transform(other_features)
lat_lon_features_scaled = StandardScaler().fit_transform(lat_lon_features)
X_train_scaled = np.hstack((lat_lon_features_scaled, other_features_scaled))

# init gaussian process regressor
kernel = C(1.0, (1e-3, 1e4)) * RBF(1.0, (1e-3, 100.0))
gpr = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=100, optimizer="fmin_l_bfgs_b")
gpr.fit(X_train_scaled, y_train)
predicted_hours = 24
new_data = np.array([[34.0600, -118.2500, 0, predicted_hours]])
new_data_scaled = scaler.transform(new_data[:, 2:])
new_data_scaled = np.hstack((new_data[:, :2], new_data_scaled))

y_pred, sigma = gpr.predict(new_data_scaled, return_std=True)

# mock starting coords
current_lat = 30.12689
current_lon = -88.47439

# Predicted changes
delta_lat_pred = y_pred[0][0]
delta_lon_pred = y_pred[0][1]

# Predicted coordinates
predicted_lat = current_lat + delta_lat_pred
predicted_lon = current_lon + delta_lon_pred
print()
print()
print(f"Starting Coordinates: LAT:{current_lat} LON:{current_lon}")
print(f"Predicted coordinates after {predicted_hours} hours: LAT:{predicted_lat} LON:{predicted_lon}")
print(f"Prediction Standard Deviation: {sigma}")
print()
distance_diff, x, y = calculate_position_change(current_lat, current_lon, predicted_lat, predicted_lon)
print(f"Distance: {distance_diff:.2f} km")