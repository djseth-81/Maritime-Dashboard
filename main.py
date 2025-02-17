from fastapi import FastAPI
app = FastAPI()


@app.get("/")
def first_example():
  '''
  Example First Fast API Example 
  '''
  return {"Example": "FastAPI"}