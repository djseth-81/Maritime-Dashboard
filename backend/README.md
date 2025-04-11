## main.py
Performs Websocket operations by handling GET and POST requests made by the client. Uses DBOperator to retrive basic information from interfacing with the PostGIS database.

## DBOperator
DBOperator is a basic Object meant to strictly operate on PostGIS tables. It uses the PyGreSQL `psycopb2` library to execute PostgreSQL calls. It only performs very basic SQL queries right now, and one entity at a time.

Below is a list of methods that the Object offers:

### DBOperator(table, host, port, user, passwd, schema, db)
Requires a table to be specified in order to define an instance. Assumes a public instance, connected to database "demo" hosted on localhost:5432 with no user logging in

### add(entity: dict)
Takes a dictionary of values to add to database

### modify(entity: dict, data: dict)
Use dictionary values to identify an existing entity to update with a dictionary of data.

### delete(entity: dict)
Takes a dictionary to identify an entity to delete from table

### clear()
Deletes all entities within the connected table

### custom_cmd(cmd: str, call: str)
Takes an SQL command as a string to execute on database. Will require 'r' or 'w' to identify proper commit() call

### commit() -> tuple
Submits changes made by add(), modify(), clear(), and delete() calls to table.

### rollback() -> tuple
Clears queued changes to table

### close() -> tuple
Closes instance

### fetch_filter_options()
Returns a dictionary of unique values associated with attributes inside a table that can be used as filterable data.

### query(entity: list[dict]) -> dict
Takes a list of dictionary values to fetch entities from current connected table

### get_table() -> list
Pulls all entities from table as a list

### get_count() -> int
Returns a count of all entities within a table

### proximity(var: str, range: float)
Returns entities in a table that are within a specified range of a geometry object. Requires the geometry attribute to be present in the table to be used.

### within(var: str)
Returns entities in a table that are inside a Polygon or Mult-Polygon. Requires the geometry attribute to be present in the table to be used.

## Processors
Processors generate and/or package data for the work with known APIs, and will push packaged data to Kafa topics and the database.

### Global Fishing Watch (GFW) APIs
These processors interact with the GFW events databases to pull various events reported by vessels. These events update values for the reporting vessel, and depending on the event, will post an event to a Kafka topic and database.

#### Encounters
The Encounter API tracks vessels that approach another vessel. This is posted as an event, and is also used to update the reporting vessel's data.

#### Fishing
The Fishing API tracks vessels reporting their fishing activity. This is used to update the reporting vessel's data.

#### Loitering
The Loitering API tracks vessels that are in limited or low movement, or have stopped out from port. These events are used to update the reporting vessel's data.

#### Ports
The Ports API track vessels entering/exiting port. It provides approaching port details, duration, and departure. These events currently only update the reporting vessel's data.

#### Transponder
The Transponder API tracks when a vessel turns off/on their AIS transponder. This is used to update the reporting vessel's data.

#### Vessels
The Vessels API pulls vessels that are tracked with the GFW database. It is currently not actively used.

### NOAA CO-OP APIs
NOAA's CO-OP station records weather and oceanographic data, which are provided as data to the dashboard.

#### Met API
The Met API makes calls to a given station's API for meteorlogical reports. It records air temperature, wind, visibility, and humidity. It also records notices that are posted by the station.

#### Oce API
The Oce API makes calls to a given station's API for oceanographic reports. It records the water temperature, wwater conductivity, water salinity, and water level.

#### Stations
The Stations API makes a call to collect all stations associated with NOAA's CO-OP program. It is not active, but will periodically udpate a station's associated datums so the other processors can make more informed reports when these stations enable or disable sensors.

### NOAA NWS APIs
NOAA's National Weather Service provides meteorlogical and forecast data for the US and its territories. 

These processors have not currently been implemented
