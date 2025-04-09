import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from ...DBOperator import DBOperator
from datetime import datetime, timedelta
import pytz

"""
// TODO
- Pull events starting this year

//Events
- Types
    - gaps : AIS transponder turns off/on, and gap between off-on status
- Update vessels reporting event
    - Speed, lat/lon, status, etc

- Start with offset = 0, update with ['nextOffset']
"""

def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    # pprint(response.json())
    return response.json()

"""
### Size of entries retrieved from API
"""
q = 100

GFW_TOKEN = os.environ.get("TOKEN")

if GFW_TOKEN == None:
    sys.exit("No GFW API Token provided.")

vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

date = datetime.now()
utc = pytz.UTC

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

data = {
    "datasets": [
        "public-global-gaps-events:latest"
    ],
    "startDate": "2025-01-01",
    "endDate": date.strftime("%Y-%m-%d"),
}

dubs = 0
failures = []

entity = {} # Empty dict for our events entity

events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit={q}"
events = requests.post(events_url, headers=headers, json=data)
print(events.status_code)

events_data = events.json()['entries']

events_keys = [i for i in events.json().keys()]
events_offset = events.json()['offset']
events_nextOffset = events.json()['nextOffset']
total_events = events.json()['total']
events_size = events.json()['limit']

print(f"Event keys: {events_keys}")
print(f"Total found events: {total_events}")
print(f"Current events offeset: {events_offset}")
print(f"next events offeset: {events_nextOffset}")
if events_nextOffset:  # If we more data waitng for us, calculate what's left
    print(f"Remaining events: {total_events - events_size}")

# Getting event at index 0
event = events_data[0]
for event in events_data:

    # Start the parse
    event_id = event['id']  # id
    startTime = event['start'] # effective
    endTime = event['end']  # expires
    startDate = datetime.fromisoformat(event['start'])
    endDate = datetime.fromisoformat(event['end'])

    # Identifiers for reporting vessel
    mmsi = event['vessel']['ssvid']
    vessel_name = event['vessel']['name']

    # Getting latitutde and longitude
    lat = event['position']['lat']
    lon = event['position']['lon']
    status = 'UNKNOWN'

    # Get type of event, and update vessel details and additional parameters
    # based off what *I* consider "quick common sense"
    event_type = event['type']
    # print(f"Event type: {event_type.upper()}")  # type

    description = f"{vessel_name} ({mmsi}) AIS transponder has stopped reporting"
    instructions = "None"  # instructions
    event_urgency = 'low'  # urgency
    event_severity = 'low'  # severity
    headline = f"AIS Transponder for {vessel_name} deactivated"  # headline

    # if event is currenty active, update with start time. If it is expired,
    # update with end. Otherwise, ignore (save to events later).
    if (utc.localize(date) > endDate):  # Event has passed
        timestamp = event['end']
        dist_from_port = event['distances']['endDistanceFromPortKm']
        dist_from_shore = event['distances']['endDistanceFromShoreKm']
    elif ((utc.localize(date) >= startDate) and (utc.localize(date) <= endDate)):  # Event is currently active
        timestamp = event['start']
        dist_from_port = event['distances']['startDistanceFromPortKm']
        dist_from_shore = event['distances']['startDistanceFromShoreKm']

    """
    Build event dictionary
    """
    entity.update({'id': event_id})
    entity.update({'src_id':mmsi}) # vessel ID
    entity.update({'timestamp':date.strftime("%Y-%m-%dT%H:%M:%S")}) # Current time
    entity.update({'effective': startTime})
    entity.update({'end_time': endTime})
    entity.update({'active': (
        (utc.localize(date) >= startDate) and (utc.localize(date) < endDate)
    )})
    entity.update({'type': event_type.upper()})
    entity.update({'description':description})
    entity.update({'expires': endTime})
    entity.update({'instructions': instructions})
    entity.update({'urgency': event_urgency})
    entity.update({'severity': event_severity})
    entity.update({'headline': headline})

    pprint(entity)
    input()

    try:
        # Adding event TODO!
        # events_operator.add(entity.copy())
        # events_operator.commit()

        # Updating related vessel TODO!
        # vessels_operator.modify(entity.copy()) # TODO: TEST!
        # vessels_operator.commit()
        dubs += 1
    except Exception as e:
        print(f"An error occured adding vessel to DB...\n{e}")
        print("This vessel caused the failure:")
        pprint(entity)
        input()
        failures.append(entity)

"""
I'm using this to add constructed entities to DB, but I imagine this is where
the Kafka stuff will go as well
"""
print(f"{dubs} total pushes to DB.")
print(f"{len(failures)} total vessels that weren't added to DB for some reason")

# TODO: DUNNO IF THE FOLLOWING ACCURATELY SAVES DATA
with open('gfw-encounters-failures.csv', 'w', newline='') as outFile:
    writer = csv.DictWriter(outFile, delimiter=',',
                            fieldnames=failures[0].keys())
    writer.writeheader()
    for goob in failures:
        writer.writerow(goob)

























