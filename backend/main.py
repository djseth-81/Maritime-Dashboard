import base64
from Crypto.Cipher import AES
from json import loads, dumps
from datetime import datetime
from DBOperator import DBOperator
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

@app.get("/")
async def welcome():
    '''
    Example First Fast API Example
    '''
    return {"Message": "Welcome to FastAPI!",
            "Retrieved": datetime.now(),
           }

@app.get("/weather/")
async def weather():
    '''
    Weather query
    '''
    return {"Message": "Weather!",
            "Retrieved": datetime.now(),
           }

@app.get("/users/")
async def users():
    '''
    Users query
    '''
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

def decrypt_password(encrypted_password, secret_key):
    encrypted_data = base64.b64decode(encrypted_password)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    return decrypted_bytes.strip().decode('utf-8')

@app.post("/addUser")
async def add_user(formData: dict):
    print(formData)
    return formData

@app.post("/login")
async def login(formData: dict):
    print(formData)
    # email = formData["email"]
    # decrypted_password = decrypt_password(formData["password"], secret_key="my-secret-key")
    return (formData)

@app.get("/vessels/")
async def query_vessels():
    '''
    <query_description>
    '''
    ### Attempt DB connection
    try:
        operator = DBOperator(table='vessels')
        print("### Fast Server: Connected to vessels table")
    except Exception:
        print("### Fast Server: Unable connect to Vessels table")
        return JSONResponse(
            status_code=500,
            content={"Error": "Unable to establish database connection"}
        )

    ### IF DB connection successful, attempt assembling payload
    print("### Fast Server: Assembling Payload...")
    try:
        payload = {"Message": "grabbing a vessel...",
                   "Retrieved": datetime.now(),
                   "Privileges": operator.get_privileges(),
                   "Total entities": operator.get_count(),
                   "Table attribuets": operator.get_attributes(),
                   "payload": operator.query(('mmsi',338457199))
                   }
        print("### Fast Server: Payload assembled.")
        return payload
    except:
        print("### Fast Server: Error assembling payload.")
        payload = JSONResponse(
            status_code=400,
            content={"Error": "Error assembling payload."}
        )
    finally:
        operator.close() # Closes table instance
        return payload

@app.get("/metadata/")
async def query_metadata():
    '''
    <query_description>
    '''
    ### Attempt DB connection
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

