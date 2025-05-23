import asyncio
import json
from pprint import pprint
from json import loads, dumps
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import connect, filter_parser
from fastapi import WebSocket, WebSocketDisconnect, FastAPI
from kafka_service.kafka_ws_bridge import connected_clients, kafka_listener, start_kafka_consumer
from kafka_service.producer import send_message
from kafka_service.consumer import *
import linearRegressionPathPrediction as linearRegressionPyFile

app = FastAPI()

# CORS Middleware Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Requests from frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def connect_to_vessels() -> DBOperator:
    """
    Connects to the 'vessels' table in the database.

    :return: DBOperator instance for interacting with the vessels table.
    :raises HTTPException: If connection fails.
    """
    try:
        db = DBOperator(table='vessels')
        print("### Fast Server: Connected to vessels table")
        return db
    except Exception as e:
        print("### Fast Server: Unable to connect to Vessels table")
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to database."
        )

@app.get("/")
async def welcome():
    """
    Handles the root endpoint.

    :return: A welcome message with the current timestamp.
    """
    return {"Message": "Welcome to FastAPI!",
            "Retrieved": datetime.now(),
           }

@app.get("/weather/")
async def weather():
    """
    Handles the weather endpoint.

    :return: A weather message with the current timestamp.
    """
    db = connect('meteorology')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            # Converting types to json throws an error now, so just providing
            # attributes themselves...
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for weather: {str(e)}")

    try:
        payload['payload'] = db.get_table()
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        # raise HTTPException(status_code=501, detail=f"Coming soon")
        raise HTTPException(status_code=500, detail=f"Error fetching Weather data: {str(e)}")

@app.get("/ocean/")
async def ocean_data():
    '''
    Oceanography query
    '''
    db = connect('oceanography')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for ocean data: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Should retrieve nothing rn
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        # raise HTTPException(status_code=501, detail=f"Coming soon")
        raise HTTPException(status_code=500, detail=f"Error fetching ocean data: {str(e)}")

@app.get("/events/")
async def pull_events():
    '''
    Events/Alerts query
    '''
    db = connect('events')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Coming soon")
        # raise HTTPException(status_code=500, detail=f"Error fetching metadata for events: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Should retrieve nothing rn
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")

@app.get("/users/")
async def users():
    """
    Handles the users endpoint.

    :return: A users message with the current timestamp.
    """
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

@app.post("/addUser")
async def add_user(formData: dict):
    """
    Adds a new user based on provided form data.

    :param formData: A dictionary containing user information.
    :return: The received form data.
    """
    print("### Websocket: Form data:")
    print(formData)
    return formData

@app.post("/login")
async def login(formData: dict):
    """
    Logs in a user based on provided form data.

    :param formData: A dictionary containing user credentials.
    :return: The received form data.
    """
    print(formData)
    # email = formData["email"]
    # decrypted_password = decrypt_password(formData["password"], secret_key="my-secret-key")
    return formData

@app.get("/stations/", response_model=dict)
async def get_stations():
    '''
    Stations query
    '''
    db = connect('sources')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            # "filters": db.fetch_filter_options(),
            "payload": []
    }
    except Exception as e:
        print(f"### Websocket: Error fetching metadata for stations:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for stations: {str(e)}")

    try:
        payload['payload'] = db.get_table() # Currently only NOAA-COOP stations in table
        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stations: {str(e)}")

@app.get("/vessels/", response_model=dict)
async def get_filtered_vessels(
    type: str = Query("", description="Filter by vessel type"),
    origin: str = Query(None, description="Filter by country of origin"),
    status: str = Query(None, description="Filter by vessel status")
):
    """
    Fetches vessel data based on filters.

    :param type: Filter by vessel type.
    :param origin: Filter by country of origin.
    :param status: Filter by vessel status.
    :return: Filtered vessel data.
    :raises HTTPException: If database interaction fails.
    """
    db = connect('vessels')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            "filters": db.fetch_filter_options(),
            "payload": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    # I'm confused here... we split types, but then we apply types in the
    # filters later to ignore emtpy filters?
    types_list = type.split(',') if type else []
    filters = {}

    if types_list:
        filters["type"] = type.split(',') if type else []
    if origin:
        filters["flag"] = origin
    if status:
        filters["current_status"] = status.split(',') if status else []

    if not types_list:
        payload['payload'] = []
        payload["size"] = 0
        return payload

    # Ignore empty filters
    filters = {key: value for key, value in {
        "type": types_list,
        "flag": origin if origin else None,
        "current_status": status if status else None
    }.items() if value}

    if len(filters) > 0:
        queries = []
        filter_parser(filters,queries)

        # NOTE: Bandaid for BAD RECURSION!
        # This is because my recursion sucks so there's a chance for duplicates
        # when more than 1 attribute has multiple values
        queries = [dict(t) for t in {tuple(d.items()) for d in queries}]

        ### IF DB connection successful, attempt assembling payload
        try:
            # Return all vessels if no filters are provided
            payload["payload"] = db.query(queries)
            payload["size"] = len(payload["payload"])
            return payload
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching vessels: {str(e)}")
    # Return all vessels if no filters are provided
    else:
        payload['payload'] = db.get_table()
        payload["size"] = len(payload["payload"])
        return payload
    db.close()

# FIXME: Weird bug where selecting a vessel and then selecting apply filters assumes zoning
# FIXME: Bug where entities inside/outside zone appear to behave as uninteded (read bug report for more)
@app.post("/zoning/", response_model=dict)
async def zone_vessels(data: dict):
    '''
    Zoning query. Collects Meteorological and oceanographic data, events,
    and vessels that are sourced from inside zone
    '''
    vessels = connect('vessels')
    met = connect('meteorology')
    oce = connect('oceanography')
    events = connect('events')
    sources = connect('sources')
    zones = connect('zones')

    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": vessels.permissions,
            "attributes": [i for i in vessels.attrs.keys()],
            "payload": {}
        }
    except Exception as e:
        print(f"### Websocket: Error fetching metadata for zoning:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    geom = data['geom']
    types = data['type'].split(',') if 'type' in data.keys() else []
    status = data['origin'].split(',') if 'origin' in data.keys() else []
    flags = data['flag'].split(',') if 'flag' in data.keys() else []

    # pprint(geom)

    try:
        ### Getting Vessels
        payload['payload'].update({'vessels':[]})

        # NOTE: I HATE this implemenetation.
        for i in vessels.within(geom):
            if (i['type'] in types) or (i['flag'] in flags) or (i['current_status'] in status):
                payload['payload']['vessels'].append(i)

        payload['size'] = len(payload['payload'])

        # Pulling stations
        stations = [i['id'] for i in sources.within(geom)]

        # Give them another chance :)
        # If the original geometry doesn't encompass stations, does it overlap
        # with known geometries?
        if len(stations) < 1:
            waah = [eek for eek in zones.overlaps(geom)]
            for wah in waah:
                stations.extend([i['id'] for i in sources.within(wah['geom'])])

        if len(stations) > 0:
            payload['payload'].update({'stations': stations} if len(stations) > 0 else {'guh!': "No stations found."})

            ### Getting Meteorology
            payload['payload'].update({'weather': met.query([{'src_id': i} for i in stations])})

            ### Getting Oceanography
            payload['payload'].update({'oceanography': oce.query([{'src_id': i} for i in stations])})

            ### Getting events
            payload['payload'].update({'alerts': events.query([{'src_id': i} for i in stations])})

        return payload

    except Exception as e:
        print(f"### Websocket: Error fetching zoning data:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching zone data: {str(e)}")
    finally:
        vessels.close()

@app.get("/filters/", response_model=dict)
async def get_filter_options():
    """
    Fetches available filter options for vessels.

    :return: A dictionary containing filter options.
    :raises HTTPException: If database interaction fails.
    """
    db = connect_to_vessels()
    try:
        filter_options = db.fetch_filter_options()
        if not filter_options:
            raise HTTPException(status_code=404, detail="No filter options found.")
        return filter_options
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filter options: {str(e)}")
    finally:
        db.close()

@app.post("/vessels/add/")
async def add_vessel(data: dict):
    """
    Adds a new vessel to the database.

    :param data: A dictionary containing vessel information.
    :return: A success message upon successful insertion.
    :raises HTTPException: If database interaction fails or required fields are missing.
    """
    db = connect_to_vessels()
    required_fields = ["id", "name", "type", "country_of_origin", "status", "latitude", "longitude"]

    if not all(field in data for field in required_fields):
        raise HTTPException(status_code=400, detail=f"Missing required fields. Required fields are: {required_fields}")

    try:
        db.add(data)
        db.commit()
        return {"status": "success", "message": "Vessel added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding vessel: {str(e)}")
    finally:
        db.close()

@app.get("/eezs/", response_model=dict)
async def fetch_eezs():
    db = connect('zones')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": db.permissions,
            "attributes": [i for i in db.attrs.keys()],
            "payload": [],
        }
        # Disgusting. FIXME
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (American Samoa)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Palmyra Atoll)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Puerto Rico)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (United States Virgin Islands)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Johnston Atoll)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Guam)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Northern Mariana Islands)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Jarvis Islands)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Howland and Baker Islands)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Hawaii)'}]))
        payload['payload'].extend(db.query([{'name':'United States Exclusive Economic Zone (Alaska)'}]))
        payload.update({"size": len(payload['payload'])})
        return payload
    except Exception as e:
        print(f"### Websocket: Error fetching data for EEZs:\n{e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data for EEZs: {str(e)}")
    finally:
        db.close()

@app.get("/predict/{lat}/{lon}/{sog}/{heading}")
async def predict_path(lat: float, lon: float, sog: float, heading: float):
    """
    Predicts vessel path based on coordinates.

    :param lon: Longitude coordinate of the vessel.
    :param lat: Latitude coordinate of the vessel.
    :param sog: Speed of vessel
    :param heading: Heading of vessel
    :return: Predicted path data as a list of dictionaries.
    :raises HTTPException: If prediction fails.
    """
    print(f"Received coordinates -  Latitude: {lat}, Longitude: {lon}")
    predictions = start_vessel_prediction(lat, lon, sog, heading)
    pprint(predictions)
    return predictions.to_dict(orient="records")

# Frontend Websocket > FastAPI backend > Kafka > Consumer
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("### WebSocket: Client connected")
    connected_clients.add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            print("Received from client:")
            pprint(data)
            await websocket.send_text(f"Echo: {data}")

            try:
                parsed = loads(data)
                key = parsed.get("key", "default")
                topic = parsed.get('topic',"Users")
                payload = parsed.get('value')
                send_message(topic, key, payload)
                print(f"Sent to Kafka | key: {key} | value: {parsed}")

            except json.JSONDecodeError:
                print(f"Received non-JSON message: {data}")
            except Exception as e:
                print(f"Error sending to Kafka: {e}")

    except WebSocketDisconnect:
        print("### WebSocket: Client disconnected")
        connected_clients.remove(websocket)

@app.on_event("startup")
async def startup_event():
    start_kafka_consumer()
    asyncio.create_task(kafka_listener())

