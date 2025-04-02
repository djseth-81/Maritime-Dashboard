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
uvicorn backend.main:app --host 0.0.0.0 --port 5000 --reload

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
