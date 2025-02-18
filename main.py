from fastapi import FastAPI
from datetime import datetime
app = FastAPI()


@app.get("/")
def welcome():
    '''
    Example First Fast API Example
    '''
    return {"Message": "Welcome to FastAPI!",
            "timestamp": datetime.now(),
           }

@app.get("/weather/")
def weatherAPI():
    '''
    Example First Fast API Example
    '''
    return {"Message": "Weather API data",
            "timestamp": datetime.now(),
           }
