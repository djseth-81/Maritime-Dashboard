# Demo env for Backend

## 1. Activate Python Virtual Environment
### Setup
`python3 -m venv {name_of_virtual_environment}`
### Activate
`source {name_of_virtual_environment}/bin/activate`

## 2. Install fastAPI & uvicorn
`pip install fastapi`
`pip install uvicorn`

## 3. Install PyGreSQL
`pip install PyGreSQL`

## 4. Start fastAPI server with command
`uvicorn main:app --reload`

## 5. Info
- http://127.0.0.1:8000/docs is the local server interactive API documentation source
- http://127.0.0.1:8000/redoc is an alternative of the above
- http://127.0.0.1:8000/ is the listening server

# main.py

Handles GET requests made to localhost:8000. Uses DBOperator to retrive basic information from interfacing with the PostGIS example database "NYC Census Data".

# DBOperator
DBOperator is a basic Object meant to strictly operate on PostGIS tables. It only performs very basic SQL queries right now.
