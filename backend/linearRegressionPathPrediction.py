import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import joblib
from geopy.distance import geodesic

def calculate_distance(row, data):
    """
    Function to calculate the curved distance between two points (geodesic) 
    """
    if row.name == 0:
        return 0
    prev_row = data.iloc[row.name - 1]
    return geodesic((prev_row['LAT'], prev_row['LON']), (row['LAT'], row['LON'])).km

def perform_prediction(vessel_data, lat_model, lon_model):
    """
    Function that loads the vessel data and trained models and pushed the data through
    the models to get a set of predicted path points (lat, long) over a given time frame
    """
    vessel_data['BaseDateTime'] = pd.to_datetime(vessel_data['BaseDateTime'])
    vessel_data = vessel_data.sort_values(by='BaseDateTime')
    vessel_data['TimeElapsed'] = (vessel_data['BaseDateTime'] - vessel_data['BaseDateTime'].min()).dt.total_seconds() / 3600.0

    last_known = vessel_data.iloc[-1]
    future_inputs = pd.DataFrame({
        'TimeElapsed': [last_known['TimeElapsed'] + i for i in range(1, 25)],
        'SOG': [last_known['SOG']] * 24,
        'COG': [last_known['COG']] * 24,
        'Heading': [last_known['Heading']] * 24
    })

    predicted_lats = lat_model.predict(future_inputs)
    predicted_lons = lon_model.predict(future_inputs)

    predictions = pd.DataFrame({
        'Hours Ahead': range(1, 25),
        'Predicted LAT': predicted_lats,
        'Predicted LON': predicted_lons
    })

    return predictions

def load_models_old():
    """
    Loads trained models used from limited data set
    """
    lat_model = joblib.load('vessel_model_lat_model_old.pkl')
    lon_model = joblib.load('vessel_model_lon_model_old.pkl')
    return lat_model, lon_model

def load_models_new():
    """
    Loads trained models used from a larger data set
    """
    lat_model = joblib.load('global_vessel_model_lat_model.pkl')
    lon_model = joblib.load('global_vessel_model_lon_model.pkl')
    return lat_model, lon_model

def predict_vessel_path_old(start_lat, start_lon, lat_model, lon_model, hours_ahead=24):
    """
    Predict vessel path using only lat and lon (not as accurate?)
    """
    time_periods = np.array([i for i in range(1, hours_ahead + 1)]).reshape(-1, 1)
    delta_lats = lat_model.predict(time_periods) - lat_model.predict([[0]])  # Delta from initial
    delta_lons = lon_model.predict(time_periods) - lon_model.predict([[0]])  # Delta from initial
    predicted_lats = start_lat + delta_lats
    predicted_lons = start_lon + delta_lons
    predictions = pd.DataFrame({
        'Hours Ahead': range(1, hours_ahead + 1),
        'Predicted LAT': predicted_lats,
        'Predicted LON': predicted_lons
    })

    return predictions

def predict_vessel_path_new(start_lat, start_lon, lat_model, lon_model, sog=10.0, heading=10.0, hours_ahead=24, cog=10.0):
    """
    Predict vessel path from a given starting lat/lon using the trained multi-feature linear regression models.
    Assumes constant values for SOG, COG, and Heading unless specified.
    """
    time_periods = np.array(range(1, hours_ahead + 1))
    feature_matrix = pd.DataFrame({
        'TimeElapsed': time_periods,
        'SOG': sog,
        'COG': cog,
        'Heading': heading
    })

    base_features = pd.DataFrame({'TimeElapsed': [0], 'SOG': sog, 'COG': cog, 'Heading': heading})
    base_lat = lat_model.predict(base_features)[0]
    base_lon = lon_model.predict(base_features)[0]
    predicted_lats = start_lat + (lat_model.predict(feature_matrix) - base_lat)
    predicted_lons = start_lon + (lon_model.predict(feature_matrix) - base_lon)

    predictions = pd.DataFrame({
        'Hours Ahead': time_periods,
        'Predicted LAT': predicted_lats,
        'Predicted LON': predicted_lons
    })

    return predictions

def start_vessel_prediction(start_lat, start_lon, sog, heading):
    """
    Function to start prediction
    """
    lat_model, lon_model = load_models_new()
    predictions = predict_vessel_path_new(start_lat, start_lon, lat_model, lon_model, sog, heading)
    return predictions

if __name__ == '__main__':
    print(start_vessel_prediction(30.12689, -88.47439, 17.7, 343))
