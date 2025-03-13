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

# Activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Kafka reciver
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload

# Start Kafka
bin/kafka-server-start.sh config/kraft/server.properties


fast interact with frontend directly
