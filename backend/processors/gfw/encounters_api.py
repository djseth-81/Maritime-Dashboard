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
    - encoutners: vessel reports encounter with other vessel, risk, distance (km) and duration
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

# Attempt to obtain token, and exit if none is found
GFW_TOKEN = os.environ.get("TOKEN")
if GFW_TOKEN is None:
    sys.exit("No GFW API Token provided.")

# Open up vessels and events tables
vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

# Get current time, and prep our UTC conversion
date = datetime.now()
utc = pytz.UTC

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

data = {
    "datasets": [
        # We CAN query encounters, fishing, loitering, ports, and gaps in one
        # go, but I get a timeout error when I do and it takes FOREVER
        "public-global-encounters-events:latest",
    ],
    "startDate": "2025-01-01",
    "endDate": date.strftime("%Y-%m-%d"),
}

dubs = 0
failures = []

entity = {}  # Empty dict for our events entities

# TODO: Loop through until no offset remains
# Get a batch of Encounter reports
events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit={q}"
events = requests.post(events_url, headers=headers, json=data)
print(events.status_code)

if events.status_code >= 400:  # A client/server error was encountered. Break!
    pprint("### GFW Encounters API: Encountered HTTP Error:")
    pprint(events.json())
    # break

# Pulling events data from response
events_data = events.json()['entries']

# Pulling metadata from response
events_keys = [i for i in events.json().keys()]
events_offset = events.json()['offset']
events_nextOffset = events.json()['nextOffset']
total_events = events.json()['total']
events_size = events.json()['limit']

# print(f"Event keys: {events_keys}")
# print(f"Total found events: {total_events}")
# print(f"Events retrieved: {events_size}")
# print(f"Current events offeset: {events_offset}")
# print(f"next events offeset: {events_nextOffset}")
# if events_nextOffset:  # If we more data waitng for us, calculate what's left
    # print(f"Remaining events: {total_events - events_size}")

# Iterate through retrieved events
for event in events_data:

    # Starting the parse
    event_id = event['id']  # id
    startTime = event['start']  # effective
    endTime = event['end']  # expires
    # Recording start/end time as DateTime object for determining active state and such
    startDate = datetime.fromisoformat(event['start'])
    endDate = datetime.fromisoformat(event['end'])

    # Get type of event, and update vessel details and additional parameters
    event_type = event['type']
    # print(f"Event type: {event_type.upper()}")  # type

    # Reporting vessel
    mmsi = event['vessel']['ssvid']
    vessel_name = event['vessel']['name']

    # Vessels encountered
    guest_vessel_name = event[event_type]['vessel']['name']
    guest_vessel_mmsi = event[event_type]['vessel']['ssvid']
    medianDistance = event[event_type]['medianDistanceKilometers']
    medianSpeed = event[event_type]['medianSpeedKnots']
    risk = event[event_type]['potentialRisk']

    description = f"Vessel {vessel_name} ({mmsi}) reported encounter with vessel {guest_vessel_name} ({guest_vessel_mmsi}) at a distance of {medianDistance}"
    instructions = "None"
    # If reported risk is true, set urgency and severity to high
    if risk:
        event_urgency = 'high'
        event_severity = 'high'
    else:
        event_urgency = 'low'
        event_severity = 'low'
    headline = f"Vessel encounter alert from {vessel_name}"

    """
    Updating associated vessel
    """
    # Getting latitutde and longitude
    lat = event['position']['lat']
    lon = event['position']['lon']
    # TODO: Update associated vessel's current_status, speed, heading, geom
    # TODO: Implement vessels.modify() !!!

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
    entity.update({
        'id': event_id,
        'src_id': mmsi,  # vessel ID
        'timestamp': date.strftime(
            "%Y-%m-%dT%H:%M:%S"),  # Current time
        'effective': startTime,
        'end_time': endTime,
        'active': (utc.localize(date) >= startDate) and (utc.localize(date) < endDate),
        'type': event_type.upper(),
        'description': description,
        'expires': endTime,
        'instructions': instructions,
        'urgency': event_urgency,
        'severity': event_severity,
        'headline': headline,
    })

    pprint(entity)
    input()

    try:
        """
        I'm using this to add constructed entities to DB, but I imagine this is
        where the Kafka stuff will go as well
        """
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

print(f"{dubs} total pushes to DB.")
print(f"{len(failures)} total vessels that weren't added to DB for some reason")

if len(failures) > 0:
    with open('gfw-encounters-failures.csv', 'w', newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',',
                                fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)
