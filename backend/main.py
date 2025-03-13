from Crypto.Cipher import AES
import base64
from fastapi import FastAPI, HTTPException, Query
from DBOperator import DBOperator
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware Setup 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Requests from frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

db = DBOperator(db='nyc', table='vessels')

@app.get("/filters/", response_model=dict)
async def get_filter_options():
    try:
        filter_options = db.fetch_filter_options()
        if not filter_options:
            raise HTTPException(status_code=404, detail="No filter options found.")
        return filter_options
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filter options: {str(e)}")

@app.get("/vessels/", response_model=list)
async def get_filtered_vessels(
    type: str = Query(None, description="Filter by vessel type"),
    origin: str = Query(None, description="Filter by country of origin"),
    status: str = Query(None, description="Filter by vessel status")
):
    """
    Fetch vessel data filter options.
    """
    # Ignore empty filters
    filters = {key: value for key, value in {
        "type": type if type else None,
        "origin": origin if origin else None,
        "status": status if status else None
    }.items() if value}

    try:
        # Return all vessels if no filters are provided
        filtered_vessels = db.fetch_filtered_vessels(filters) if filters else db.get_table()

        if not filtered_vessels:
            return []  # Return an empty list  
        return filtered_vessels
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching filtered vessels: {str(e)}")


@app.post("/vessels/add/")
async def add_vessel(data: dict):
    required_fields = ["id", "name", "type", "country_of_origin", "status", "latitude", "longitude"]

    if not all(field in data for field in required_fields):
        raise HTTPException(status_code=400, detail=f"Missing required fields. Required fields are: {required_fields}")

    try:
        db.add(data)
        db.commit()
        return {"status": "success", "message": "Vessel added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding vessel: {str(e)}")

# placeholder method just to communicate with frontend, need to implement fully
@app.post("/addUser")
async def add_user(formData: dict):
    print(formData)
    return formData

# placeholder method just to communicate with frontend, need to implement fully
@app.post("/login")
async def login(formData: dict):
    print(formData)
    # email = formData["email"]
    # decrypted_password = decrypt_password(formData["password"], secret_key="my-secret-key")
    return (formData)

# need to implement a standardized encryption/decryption method, placeholder for now
def decrypt_password(encrypted_password, secret_key):
    encrypted_data = base64.b64decode(encrypted_password)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    return decrypted_bytes.strip().decode('utf-8')