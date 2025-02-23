from fastapi import FastAPI
from datetime import datetime
from DBOperator import DBOperator
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

@app.get("/streets/")
def query_streets():
    '''
    <query_description>
    '''

    operator = DBOperator(db=db,table='nyc_streets')

    return {"Message": "NYC street data",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/census/")
def query_census():
    '''
    <query_description>
    '''

    operator = DBOperator(db=db,table='nyc_census_blocks')

    return {"Message": "NYC Census blocks",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/homicides/")

def query_homicides():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_homicides')

    return {"Message": "Data on NYC homicide reports",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/neighborhoods/")
def query_neighborhoods():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_homicides')

    return {"Message": "NYC neighborhood data",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/subway_stations/")

def query_subway_stations():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='nyc_subway_stations')

    return {"Message": "NYC Subway Station data",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/geometry/")

def query_geom():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='geometries')

    return {"Message": "geometry data",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }

@app.get("/metadata/")

def query_metadata():
    '''
    <query_description>
    '''
    operator = DBOperator(db=db,table='spatial_ref_sys')

    return {"Message": "Metadata on NYC census data",
            "Retrieved": datetime.now(),
            "Privileges": [
                operator.check_privileges("insert"),
                operator.check_privileges("select"),
                operator.check_privileges("update"),
                operator.check_privileges("delete")
            ],
            "Total entities": operator.get_count(),
            "Table attribuets": operator.get_attributes(),
            "payload": operator.get_table()[0]
           }
