from fastapi import FastAPI
from datetime import datetime
from DBOperator import DBOperator
from json import loads, dumps
from fastapi.middleware.cors import CORSMiddleware
from Crypto.Cipher import AES
import base64

# from kafka import KafkaProducer
db = 'nyc'
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],   # Allow all headers
)

# producer = KafkaProducer(bootstrap_servers='localhost:9092')

# @app.post("/publish/{topic}")
# def publish(topic: str, message: str):
#     producer.send(topic, message.encode())
#     return{"status": "message published successfully"}

@app.get("/")
def welcome():
    '''
    Example First Fast API Example
    '''
    return {"Message": "Welcome to FastAPI!",
            "Retrieved": datetime.now(),
           }

@app.get("/weather/")
def weather():
    '''
    Weather query
    '''
    return {"Message": "Weather!",
            "Retrieved": datetime.now(),
           }

@app.get("/users/")
def users():
    '''
    Users query
    '''
    return {"Message": "Getting users!",
            "Retrieved": datetime.now(),
           }

@app.get("/streets/")
def query_streets():
    '''
    <query_description>
    '''

    operator = DBOperator(db=db,table='nyc_streets')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC street data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('id',4))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/census/")
def query_census():
    '''
    <query_description>
    '''

    operator = DBOperator(db=db,table='nyc_census_blocks')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC street data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('gid',1))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/homicides/")
def query_homicides():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_homicides')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC street data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('gid',1))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/neighborhoods/")
def query_neighborhoods():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_neighborhoods')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC Homicide data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('gid',1))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/subway_stations/")
def query_subway_stations():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_subway_stations')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC Subway Station data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('id',1))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/geometry/")
def query_geom():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='geometries')

    print("### Server: Assembling Payload...")
    payload = {"Message": "NYC geometric data",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.custom_cmd("SELECT * FROM geometries LIMIT 1;", 'r')
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

@app.get("/metadata/")
def query_metadata():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='spatial_ref_sys')

    print("### Server: Assembling Payload...")
    payload = {"Message": "Metadata for NYC dataset",
            "Retrieved": datetime.now(),
            "Privileges": operator.get_privileges(),
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.query(('srid',26918))
           }
    print("### Server: Payload assembled.")
    operator.close() # Closes table instance
    return payload

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