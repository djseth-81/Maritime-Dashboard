from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from backend.linearRegressionPathPrediction import (
    calculate_distance,
    perform_prediction,
    load_models_old,
    load_models_new,
    predict_vessel_path_old,
    predict_vessel_path_new,
    start_vessel_prediction
)

def test_calculate_distance():
    # sample DataFrame with LAT, LON values
    data = pd.DataFrame({
        'LAT': [30.0, 30.1, 30.2],
        'LON': [-90.0, -90.1, -90.2]
    })

    # test for row at index 1 (simulate row in DataFrame)
    row = data.iloc[1]

    distance = calculate_distance(row, data)
    assert isinstance(distance, float)

def test_perform_prediction():
    vessel_data = pd.DataFrame({
        'BaseDateTime': ['2021-01-01 00:00', '2021-01-01 01:00'],
        'SOG': [10.0, 12.0],
        'COG': [90.0, 90.0],
        'Heading': [90.0, 90.0],
        'LAT': [30.0, 30.1],
        'LON': [-90.0, -90.1]
    })
    vessel_data['BaseDateTime'] = pd.to_datetime(vessel_data['BaseDateTime'])
    lat_model = MagicMock()
    lon_model = MagicMock()
    lat_model.predict.return_value = [30.2] * 24
    lon_model.predict.return_value = [-90.2] * 24
    
    result = perform_prediction(vessel_data, lat_model, lon_model)
    
    assert isinstance(result, pd.DataFrame)
    assert 'Predicted LAT' in result.columns
    assert 'Predicted LON' in result.columns

@patch('joblib.load')
def test_load_models_old(mock_load):
    lat_model = MagicMock()
    lon_model = MagicMock()
    mock_load.side_effect = [lat_model, lon_model]
    lat, lon = load_models_old()
    
    assert lat == lat_model
    assert lon == lon_model

@patch('joblib.load')
def test_load_models_new(mock_load):
    lat_model = MagicMock()
    lon_model = MagicMock()
    mock_load.side_effect = [lat_model, lon_model]
    lat, lon = load_models_new()
    
    assert lat == lat_model
    assert lon == lon_model

@patch('sklearn.linear_model.LinearRegression.predict')
def test_predict_vessel_path_old(mock_predict):
    mock_predict.return_value = np.array([30.2, 30.3, 30.4])
    lat_model = LinearRegression()
    lon_model = LinearRegression()
    start_lat = 30.0
    start_lon = -90.0
    hours_ahead = 3
    
    result = predict_vessel_path_old(start_lat, start_lon, lat_model, lon_model, hours_ahead)
    
    assert isinstance(result, pd.DataFrame)
    assert 'Predicted LAT' in result.columns
    assert 'Predicted LON' in result.columns
    assert result.shape[0] == hours_ahead

@patch('sklearn.linear_model.LinearRegression.predict')
def test_predict_vessel_path_new(mock_predict):
    mock_predict.return_value = np.array([30.2, 30.3, 30.4])
    lat_model = LinearRegression()
    lon_model = LinearRegression()
    start_lat = 30.0
    start_lon = -90.0
    sog = 10.0
    heading = 10.0
    hours_ahead = 3
    cog = 10.0
    
    result = predict_vessel_path_new(start_lat, start_lon, lat_model, lon_model, sog, heading, hours_ahead, cog)
    
    assert isinstance(result, pd.DataFrame)
    assert 'Predicted LAT' in result.columns
    assert 'Predicted LON' in result.columns
    assert result.shape[0] == hours_ahead

@patch('backend.linearRegressionPathPrediction.load_models_new')
@patch('backend.linearRegressionPathPrediction.predict_vessel_path_new')
def test_start_vessel_prediction(mock_predict, mock_load_models):
    lat_model = MagicMock()
    lon_model = MagicMock()
    
    mock_load_models.return_value = (lat_model, lon_model)
    mock_predict.return_value = pd.DataFrame({
        'Hours Ahead': [1, 2, 3],
        'Predicted LAT': [30.1, 30.2, 30.3],
        'Predicted LON': [-90.1, -90.2, -90.3]
    })
    
    result = start_vessel_prediction(30.0, -90.0, 10.0, 10.0)
    
    assert isinstance(result, pd.DataFrame)
    assert 'Predicted LAT' in result.columns
    assert 'Predicted LON' in result.columns
    assert result.shape[0] == 3

