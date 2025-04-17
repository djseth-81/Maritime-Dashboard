# About
Northrop Grumman - Capstone 2025 - Maritime Operations Monitoring Dashboard

<br />

# Configuring Environment
## 1. Activate Python Virtual Environment
### Setup
`python3 -m venv {name_of_virtual_environment}`
### Activate
`source {name_of_virtual_environment}/bin/activate`

<br />

## 2. Install fastAPI & uvicorn
`pip install fastapi`
`pip install uvicorn`

<br />

## 3. Install PyGreSQL
`pip install PyGreSQL`

<br />

## 4. Running FastAPI (cd into backend directory)
`uvicorn main:app --reload`

### Backend Info
- http://127.0.0.1:8000/docs is the local server interactive API documentation source
- http://127.0.0.1:8000/redoc is an alternative of the above
- http://127.0.0.1:8000/ is the listening server

<br />

## 5. Installing React & Dependencies
### Node Package Manager (npm) Installation Instructions
- [Windows Link](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [MacOS Link](https://formulae.brew.sh/formula/node)
- [Linux Link](http://www.blankwebsite.com)

### Initialize & Install Dependencies
`npm init -y`

`npm install react react-dom`

`npm install cesium resium`

`npm install --save-dev vite @vitejs/plugin-react vite-plugin-cesium`

`npm install react-toastify axios`

### Run Dev Server
`npm run dev`

# Activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Kafka reciver
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload


# Start Kafka
bin/kafka-server-start.sh config/kraft/server.properties


fast interact with frontend directly

<br />

# Release Notes
## v1.0
### Features
- CesiumJS Implementation of a 2D/3D Map
- Initial FastAPI and Database Setup
- Interactable UI with initial geometry and filters
- [UI Design Plan](https://balsamiq.cloud/sp2vjb1/p94nxql/r2278)

### Bug Fixes
- N/A
### Other
- N/A

## v2.0
### Features
- Improved filter component to be more efficient and useful
- Setup local database and a centralized SQL database server for data management
- Setup Kafka server alonside database server
- Initial path prediction models have been setup

### Bug Fixes
- Fixed issue with vessel positions not converting coordinates correctly between 2D and 3D maps
- Fixed issue with shapes weren't being displayed on the map as intended
- Fixed issue where providing multple values for filters returned no ships
  
### Other
- N/A



## Notes for Yolvin
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (msg) => console.log("Message from server:", msg.data);
ws.onopen = () => {
  console.log("WebSocket connection opened");
};
ws.onclose = () => console.log("WebSocket closed");
ws.onerror = (e) => console.error("WebSocket error:", e);



ws.send(JSON.stringify({ key: "shipX", status: "All clear" }));


## GFW Token
$env:TOKEN="x"

## Consumer Listner
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic maritime-events --from-beginning


python -m backend.processors.gfw.loitering_api
python -m backend.processors.gfw.fishing_api
python -m backend.processors.gfw.encounters_api
python -m backend.processors.gfw.ports_api
python -m backend.processors.gfw.transponder_api
python -m backend.processors.gfw.vessels_api