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
    - loitering: start/stop loiterings status
- Update vessels reporting event
    - Speed, lat/lon, status, etc

- Start with offset = 0, update with ['nextOffset']

"""
def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    # pprint(response.json())
    return response.json()

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
        "public-global-loitering-events:latest",
    ],
    "startDate": "2024-01-01",
    "endDate": date.strftime("%Y-%m-%d"),
}

entity = {} # Empty dict for our events entities

events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
events = requests.post(events_url, headers=headers, json=data)
print(events.status_code)
pprint(events.json()['entries'])
pprint(events.json().keys())
sys.exit()

# Retrieving more details with latest events

"""
Getting Events reported by vesesel. It has some data that is used for
vessels table
"""
events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
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

event_id = event['id']  # id
startTime = event['start'] # effective
endTime = event['end']  # expires

# pprint(event)
# input()

# Getting latitutde and longitude
lat = event['position']['lat']
lon = event['position']['lon']

# Get type of event, and update vessel details and additional parameters
# based off what *I* consider "quick common sense"
event_type = event['type']
print(f"Event type: {event_type.upper()}")  # type

speed = event[event_type]['averageSpeedKnots']
if speed == 0:
    status = 'LOITERING'
else:
    status = 'LIMITED MOVEMENT'
description = f"{vessel_name} ({mmsi}) has been reported loitering"
instructions = "None"  # instructions
event_urgency = 'low'  # urgency
event_severity = 'low'  # severity
headline = f"{vessel_name} found loitering"  # headline
event_urgency = 'low'  # urgency
event_severity = 'low'  # severity

# if event is currenty active, update with start time. If it is expired,
# update with end. Otherwise, ignore (save to events later).
startDate = datetime.fromisoformat(event['start'])
endDate = datetime.fromisoformat(event['end'])
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
entity.update({'src_id':event['vessel']['ssvid']}) # vessel ID
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

