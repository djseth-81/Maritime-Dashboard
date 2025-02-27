# Maritime-Ops-Dashboard
Northrop Grumman - Capstone 2025 - Maritime Operations Monitoring Dashboard

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

## 4. Running FastAPI
### Start fastAPI server with command (in backend directory)
`uvicorn main:app --reload`

## 5. Installing React & Dependencies
### Node Package Manager (npm) is required
- [Windows Link](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [MacOS Link](https://formulae.brew.sh/formula/node)
- [Linux Link](http://www.blankwebsite.com)

### Initialize & Install Dependencies
`npm init -y`
`npm install react react-dom`
`npm install cesium resium`
`npm install --save-dev vite @vitejs/plugin-react vite-plugin-cesium`
`npm install react-toastify`

### Run Dev Server
`npm run dev`

### Backend Info
- http://127.0.0.1:8000/docs is the local server interactive API documentation source
- http://127.0.0.1:8000/redoc is an alternative of the above
- http://127.0.0.1:8000/ is the listening server