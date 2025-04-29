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

<br />

## 5. Python Documentation Tool Init

### Install Sphinx Library

`pip install sphinx`

### Optional Extensions

`pip install sphinx-autodoc-typehints`

`pip install sphinxcontrib-httpdomain`

`pip install sphinx-rtd-theme`

### Go into the main project directory

`cd MyProject`

`sphinx-quickstart docs`

### Go through the setup

add .bst files for any directories to be parsed (frontend and backend in our case)
build documenation by going into docs directory and running the make html command

`cd docs`
`make html`

### Clean Command 

`make clean`


### To push pages to github

`make html`

copy docs/build/html contents to /docs on main repo branch

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




## Notes for Yolvin
const ws = new WebSocket("ws://localhost:8000/ws");

ws.onmessage = (msg) => console.log("Message from server:", msg.data);
ws.onopen = () => {
  console.log("WebSocket connection opened");
};
ws.onclose = () => console.log("WebSocket closed");
ws.onerror = (e) => console.error("WebSocket error:", e);



ws.send(JSON.stringify({ key: "shipX", status: "All clear" }));

----------------------------------------GFW--------------------------------------------------------
## GFW Token
$env:TOKEN="x"

## Consumer Listner
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic GFW --from-beginning



python -m backend.processors.gfw.loitering_api
python -m backend.processors.gfw.fishing_api
python -m backend.processors.gfw.encounters_api
python -m backend.processors.gfw.ports_api
python -m backend.processors.gfw.transponder_api
python -m backend.processors.gfw.vessels_api


----------------------------------------NWS--------------------------------------------------------
## Consumer Listner
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic NWS --from-beginning



python -m backend.processors.nws.alerts_api
python -m backend.processors.nws.met_api


----------------------------------------Live Vessel Tracking Startup--------------------------------------------------------
.\.venv\Scripts\activate 
pip install pytz requests kafka-python

python -m backend.processors.gfw.gfw_runner







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

## v3.0
### Features
- Infobox now shows additional information pertaining on the entity selected
- Improved path prediction model to use extra features in the model for better prediction accuracy
- API processors gather and package event data from the Global Fishing watch Encounters, Fishing, Loitering, AIS Transponder Gaps, and Port visits events databases
- API processors gather and package oceanography and meteorology data from NOAA CO-OP
- Added a legend for visibility
- Modularized the codebase to ease bug-fixing and adding new features

### Bug Fixes
- Fixed issue with vessels not being as visible
- Fixed issue with infobox description
- Fixed issue with backend operations where they weren't agnostic to different table attributes in the database
- Added troubleshooting various error messages thrown
- Real-time messaging pipeline to pass data from the frontend over to Kafka and then listens to those messages with a Kafka consumer
  
### Other
- Known Bugs
  - Vessels flash on UI when toggling filters while zoning function is applied
  - Custom zoning may include and/or exclude vessels that would appear otherwise when applied
- Got the frontend to pass data via WebSocket which the backend pushed it to Kafka and stores it as a topic
  - Then have a consumer listening that manages the message

## v4.0
### Features
- API processors retrieve and package NOAA NWS forecast and alert data
- Kafka integration enables websocket to retrieve data from API processors
- Path prediction improved to match vessel direction
- Weather overlay component for visualizing cloud cover, wind, and rain using University of Iowa and OpenWeatherMap APIs
- Exclusive Economic Zone overlay component to display US EEZ boundaries retrieved from database
- Vessel visualization updated for clarity

### Bug Fixes
- Custom zones not containing a station would error out with no data.
- Undo option fixed when defining custom geometry
- Infobox not being visible

### Other
- OpenWeatherMap API is rate limited so is not real-time
- User login and account management were shelved
- Saving custom presets were shelved
- Bugs
  - EEZ zones and custom geometry zones collide, where one appears to override the other when displayed
