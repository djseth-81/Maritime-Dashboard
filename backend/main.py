from fastapi import FastAPI
from datetime import datetime
from DBOperator import DBOperator
from json import loads, dumps

from kafka import KafkaProducer

app = FastAPI()

db = 'nyc'

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
