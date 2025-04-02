from pprint import pprint
from json import loads, dumps
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from utils import connect, decrypt_password, filter_parser

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
    return {"Message": "Weather!",
            "Retrieved": datetime.now(),
           }

@app.get("/users/")
async def users():
    """
    Handles the users endpoint.

    :return: A users message with the current timestamp.
    """
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

def decrypt_password(encrypted_password: str, secret_key: str) -> str:
    """
    Decrypts a password using AES encryption.

    :param encrypted_password: The base64-encoded encrypted password.
    :param secret_key: The encryption key used for decryption.
    :return: The decrypted password as a string.
    """
    encrypted_data = base64.b64decode(encrypted_password)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    return decrypted_bytes.strip().decode('utf-8')

@app.post("/addUser")
async def add_user(formData: dict):
    """
    Adds a new user based on provided form data.

    :param formData: A dictionary containing user information.
    :return: The received form data.
    """
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
    

def filter_parser(p: dict, result: list) -> None:
    """
    Recursively generates query options from filter parameters.
    ### WARNING: Creates some duplicate queries when more than one attribute
    has more than 1 value. Pretty sure its cuz my recursive restraints suck. 
    Shouldn't affect results since its a UNION query

    :param p: Dictionary containing filter criteria.
    :param result: List to store the resulting filter options.
    """
    x = {}
    for k, v in p.items():
        val = v if isinstance(v, list) else v.split(',')
        while len(val) > 1:
            q = p.copy()
            q[k] = val.pop(0)
            filter_parser(q, result)
        x.update({k: val[0]})
    result.append(x)

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
            "attribuets": db.attrs,
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
        print("### Fast Server: All vessel types unchecked → Returning empty payload.")
        payload['payload'] = []
        payload["size"] = 0
        return payload

    print("### Fast Server: Assembling Payload...")
    # Ignore empty filters
    filters = {key: value for key, value in {
        "type": types_list,
        "flag": origin if origin else None,
        "current_status": status if status else None
    }.items() if value}

    print(f"### Websocket: Filters:\n{filters}")
    if len(filters) > 0:
        queries = []
        filter_parser(filters,queries)

        # NOTE: Bandaid for BAD RECURSION!
        # This is because my recursion sucks so there's a chance for duplicates
        # when more than 1 attribute has multiple values
        queries = [dict(t) for t in {tuple(d.items()) for d in queries}]

        print(f"### Websocket: query array:")
        pprint(queries)

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
@app.post("/zoning/")
async def zone_vessels(data: dict):
    vessels = connect('vessels')
    met = connect('meteorology')
    oce = connect('oceanography')
    events = connect('events')
    try:
        payload = {
            "retrieved": datetime.now(),
            "privileges": vessels.permissions,
            "attribuets": vessels.attrs,
            "payload": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata for vessels: {str(e)}")

    geom = data['geom']
    types = data['type'].split(',') if 'type' in data.keys() else []
    status = data['origin'].split(',') if 'origin' in data.keys() else []
    flags = data['flag'].split(',') if 'flag' in data.keys() else []

    try:

        # NOTE: I HATE this implemenetation.
        # Would like to pop FROM query instead of append to results
        # but it does some weird shit rn
        query = vessels.within(geom)

        for i in query:
            if (i['type'] in types) or (i['flag'] in flags) or (i['current_status'] in status):
                payload['payload'].append(i)

        payload['size'] = len(payload['payload'])
        return payload
    except Exception as e:
        raise HTTPException(status_code=501, detail=f"Zoning not implemeneted")
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

@app.get("/metadata/")
async def query_metadata():
    """
    Fetches metadata for spatial reference systems.

    :return: Metadata payload including privileges, entity count, and attributes.
    :raises HTTPException: If database interaction fails.
    """
    try:
        operator = DBOperator(table='spatial_ref_sys')
    except:
        print("### Fast Server: Unable connect to spatial_ref_sys table")
        return JSONResponse(
            status_code=500,
            content={"Error": "Unable to establish database connection"}
        )

    ### IF DB connection successful, attempt assembling payload
    print("### Server: Assembling Payload...")
    try:
        payload = {"Message": "Metadata for Geometry",
                   "Retrieved": datetime.now(),
                   "Privileges": operator.get_privileges(),
                   "Total entities": operator.get_count(),
                   "Table attribuets": operator.get_attributes(),
                   "payload": operator.query(('srid',4326)) # Spatial reference system, Global scope (https://spatialreference.org/ref/epsg/4326/)
                   }
        print("### Server: Payload assembled.")
    except:
        print("### Fast Server: Error assembling payload.")
        payload = JSONResponse(
            status_code=400,
            content={"Error": "Error assembling payload."}
        )
    finally:
        operator.close() # Closes table instance
        return payload
    
@app.get("/prediction/{lon}/{lat}")
async def predict_path(lon: float, lat: float):
    """
    Predicts vessel path based on coordinates.

    :param lon: Longitude coordinate of the vessel.
    :param lat: Latitude coordinate of the vessel.
    :return: Predicted path data as a list of dictionaries.
    :raises HTTPException: If prediction fails.
    """
    print(f"Received coordinates - Longitude: {lon}, Latitude: {lat}")
    # linear_regression.perform_training_manually()
    predictions = linear_regression_2.perform_vessel_prediction(lat, lon)
    return predictions.to_dict(orient="records")
