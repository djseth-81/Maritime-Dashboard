# Demo env for Backend

## 1. Activate Python Virtual Environment
### Setup
`python3 -m venv {name_of_virtual_environment}`
### Activate
`source {name_of_virtual_environment}/bin/activate`

## 2. Install fastAPI & uvicorn
`pip install fastapi`

`pip install uvicorn`

## 3. Create main.py file
Format should be similar to below

```
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def first_example():
  '''
  Example First Fast API Example 
  '''
  return {"Example": "FastAPI"}
```

## 4. Start fastAPI server with command
`uvicorn main:app --reload`

## 5. Info
- http://127.0.0.1:8000/docs is the local server interactive API documentation source
- http://127.0.0.1:8000/redoc is an alternative of the above
- http://127.0.0.1:8000/ is the listening server
