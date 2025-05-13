from unittest.mock import patch, MagicMock
from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_welcome():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Message": "Hello :)"}

@patch("backend.main.connect")
def test_weather(mock_connect):
    mock_db = MagicMock()
    mock_db.permissions = ["read"]
    mock_db.attrs = {"temp": "float", "humidity": "int"}
    mock_db.get_table.return_value = []
    mock_connect.return_value = mock_db

    response = client.get("/weather/")
    assert response.status_code == 200
    assert "attributes" in response.json()
    assert response.json()["size"] == 0

@patch("backend.main.connect")
def test_ocean_data(mock_connect):
    mock_db = MagicMock()
    mock_db.permissions = ["read"]
    mock_db.attrs = {"depth": "float"}
    mock_db.get_table.return_value = []
    mock_connect.return_value = mock_db

    response = client.get("/ocean/")
    assert response.status_code == 200
    assert "attributes" in response.json()

@patch("backend.main.connect")
def test_get_stations(mock_connect):
    mock_db = MagicMock()
    mock_db.permissions = ["read"]
    mock_db.attrs = {"station_id": "str"}
    mock_db.get_table.return_value = []
    mock_connect.return_value = mock_db

    response = client.get("/stations/")
    assert response.status_code == 200
    assert "attributes" in response.json()

@patch("backend.main.connect")
def test_get_filtered_vessels_no_filter(mock_connect):
    mock_db = MagicMock()
    mock_db.permissions = ["read"]
    mock_db.attrs = {"type": "str"}
    mock_db.get_table.return_value = []
    mock_db.fetch_filter_options.return_value = {}
    mock_connect.return_value = mock_db

    response = client.get("/vessels/?type=")
    assert response.status_code == 200
    assert response.json()["size"] == 0

@patch("backend.main.connect")
def test_add_vessel_success(mock_connect):
    mock_db = MagicMock()
    mock_connect.return_value = mock_db

    vessel_data = {
        "id": "V123",
        "name": "Test Vessel",
        "type": "Cargo",
        "country_of_origin": "USA",
        "status": "Active",
        "latitude": 34.5,
        "longitude": -120.5
    }

    response = client.post("/vessels/add/", json=vessel_data)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@patch("backend.main.connect")
def test_get_filter_options(mock_connect):
    mock_db = MagicMock()
    mock_db.fetch_filter_options.return_value = {"type": ["Cargo", "Fishing"]}
    mock_connect.return_value = mock_db

    response = client.get("/filters/")
    assert response.status_code == 200
    assert "type" in response.json()

@patch("backend.linearRegressionPathPrediction.start_vessel_prediction")
@patch("backend.main.connect")
def test_predict_with_model(mock_connect, mock_predict):
    mock_db = MagicMock()
    mock_connect.return_value = mock_db
    
    # mock return object
    mock_predict.return_value.to_dict.return_value = {"predicted_lat": 34.1, "predicted_lon": -119.9}
    
    lat, lon, sog, heading = 34.0, -120.0, 10.0, 90.0
    
    response = client.get(f"/predict/{lat}/{lon}/{sog}/{heading}")
    
    assert response.status_code == 200
    assert response.json() == {"predicted_lat": 34.1, "predicted_lon": -119.9}
