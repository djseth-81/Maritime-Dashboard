# Seth's Workspace for Backend

So you all can watch me break things in semi-real time :^)

# Configuring environment
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

# Running FastAPI
### Navigate to backend directory

### Start fastAPI server with command
`uvicorn main:app --reload`

### Info
- http://127.0.0.1:8000/docs is the local server interactive API documentation source
- http://127.0.0.1:8000/redoc is an alternative of the above
- http://127.0.0.1:8000/ is the listening server
