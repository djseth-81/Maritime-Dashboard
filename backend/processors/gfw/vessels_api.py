import pytz
import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from datetime import datetime, timedelta
from ...DBOperator import DBOperator

"""
IGNORE ME! As of right now, now new vessels are shared via this API. Until I
can get a consistent stream of new Vessels to report, this is ONLY to add these
vessels from scratch!

// Uh oh
- Noticed that a vessel's MMSI can change
    - Their IMO does not, tho
    - GFW states it's because the vessel can change AIS transmission, or
        - inconsistently transmit the same ID values
        - change owners, callsign, or transmitters
"""

def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    # pprint(response.json())
    return response.json()


GFW_TOKEN = os.environ.get("TOKEN")

if GFW_TOKEN is None:
    sys.exit("No GFW API Token provided.")

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

data = {
    "datasets": [
        "public-global-fishing-events:latest",
        "public-global-encounters-events:latest",
        "public-global-loitering-events:latest",
        "public-global-port-visits-events:latest",
        "public-global-gaps-events:latest"
    ],
    # "startDate": "2025-03-09",
    # "endDate": "2025-03-10",
}

vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

date = datetime.now()
utc = pytz.UTC

vessel_payload = []

# AIS Vessel search
vessels_url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search?query=mmsi&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
vessels = query(vessels_url)

# Parsing the response
payload_size = vessels['limit']
total = vessels['total']
keys = [i for i in vessels.keys()]

# Some quick metadata that may help
print(f"Entries retrieved: {payload_size}")
print(f"Total number of entries: {total}")
print(f"Entries remaining: {total - payload_size}")
print(f"Response keys: {keys}")

# Pull out all vessels found from responses
entries = vessels['entries']

"""
Iterating through Vessels found
"""
for entry in entries:
    entity = {}  # Empty dict to add to DB

    """
    Parse vessel data we currently have
    """
    # Parse combinedSourcesInfo for latest reported data.
    # Looks like most recent entry is last element in array
    index = 0
    diff = date.year
    for i, item in enumerate(entry['combinedSourcesInfo']):
        # If difference is smaller than previously recorded one, update
        if (date.year - item['shiptypes'][0]['yearTo']) < diff:
            diff = date.year - item['shiptypes'][0]['yearTo']
            # print(f"Replacing index= {index} with more recent index= {i}")
            index = i

    # Saving vessel type
    vessel_type = entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']

    # Parse selfReportedInfo for latest reported data
    # Looks like most recent entry is first element in array
    index = 0
    diff = timedelta(days=date.year)
    for i, item in enumerate(entry['selfReportedInfo']):
        startDate = datetime.fromisoformat(item['transmissionDateFrom'])
        endDate = datetime.fromisoformat(item['transmissionDateTo'])
        # If date differential is smaller than recorded one, entry is more recent. Update!
        if (utc.localize(date) - endDate <= diff):
            # print(f"Replacing old index= {index} with new index= {i}")
            diff = endDate - utc.localize(date)
            index = i

    # Parsing selfReportedInfo for various required details
    callsign = entry['selfReportedInfo'][index]['callsign']
    flag = entry['selfReportedInfo'][index]['flag']
    vessel_name = entry['selfReportedInfo'][index]['shipname']
    src = f"GFW-{entry['selfReportedInfo'][index]['sourceCode'][0]}"
    mmsi = entry['selfReportedInfo'][index]['ssvid']
    # This will update based on if event is in the past or is currently happening
    startDate = datetime.fromisoformat(
        entry['selfReportedInfo'][index]['transmissionDateFrom'])
    endDate = datetime.fromisoformat(
        entry['selfReportedInfo'][index]['transmissionDateTo'])
    if (utc.localize(date) > endDate):  # Event has passed
        timestamp = entry['selfReportedInfo'][index]['transmissionDateTo']
    elif ((utc.localize(date) >= startDate) and (utc.localize(date) <= endDate)):  # Event is currently active
        timestamp = entry['selfReportedInfo'][index]['transmissionDateFrom']

    """
    Getting Events reported by vesesel. It has some data that is used for
    vessels table
    """
    print("### Getting EVENTS ###")

    # Retrieving more details with latest events
    data.update({"vessels": [entry['selfReportedInfo'][index]['id']]})
    events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
    events = requests.post(events_url, headers=headers, json=data)
    print(f"STATUS: {events.status_code}")

    # Events response metadata
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

    # I need the most recent reported event in order to fill out the rest of
    # our data. If there isn't one, then we're just gonna ignore the vessel
    if total_events < 1:
        print(f"Skipping adding {vessel_name}. Not enough data.")
        continue

    # Parse events found for latest vessel data
    # Looks like most recent entry is first element in array
    # I'd love to make this a function, but idk how to expect different
    # dictionary keys
    index = 0
    diff = timedelta(days=date.year)
    for i, event in enumerate(events_data):
        startDate = datetime.fromisoformat(event['start'])
        endDate = datetime.fromisoformat(event['end'])
        # print(f"event Start: {startDate}, event End: {endDate}")
        if (utc.localize(date) - endDate <= diff):
            print(f"Replacing old index= {index} with new index= {i}")
            diff = endDate - utc.localize(date)
            index = i

    # Getting most recent event
    event = events_data[index]

    # pprint(event)
    # input()

    # Getting latitutde and longitude
    lat = event['position']['lat']
    lon = event['position']['lon']

    # Get type of event, and update vessel details and additional parameters
    # based off what *I* consider "quick common sense"
    event_type = event['type']
    # print(f"Event type: {event_type.upper()}")  # type

    # NOTE: I want to condense this GOD AWFUL IF BLOCKING and the past/current/future event categories
    if event_type.upper() == "ENCOUNTER":  # Encounter alert
        description = f"Vessel {vessel_name} ({mmsi}) reported encounter with the following vessels:\nVESSELS"
        instructions = "None"  # instructions
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity
        headline = f"Vessel encounter alert from {vessel_name}"  # headline

    elif event_type.upper() == "GAP":  # AIS Disabled alert
        description = f"AIS transponder disabled for {vessel_name} ({mmsi})"
        instructions = "None"  # instructions
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity
        headline = f"AIS Transponder disabled for {vessel_name}"  # headline
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity

    elif event_type.upper() == 'PORT_VISIT':
        speed = 0
        heading = 0
        status = 'ANCHORED'
        description = f"{vessel_name} ({mmsi}) visits port PORT"
        instructions = "None"  # instructions
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity
        headline = f"{vessel_name} visits port :)"  # headline
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity

    elif event_type.upper() == 'LOITERING':
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

    elif event_type.upper() == 'FISHING':
        speed = event[event_type]['averageSpeedKnots']
        status = 'FISHING'
        description = f"{vessel_name} ({mmsi}) has engaged in fishing"
        instructions = "None"  # instructions
        event_urgency = 'low'  # urgency
        event_severity = 'low'  # severity
        headline = f"{vessel_name} Fishing notice"  # headline
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

    else:
        print("// TODO: SAVE TO EVENTS")  # Maybe not
        print(f"Event type: {event_type.upper()}")  # type
        if event_type.upper() == "ENCOUNTER":  # Encounter alert
            description = f"Vessel {vessel_name} reported encounter with the following vessels:\nVESSELS"
            instructions = "None"  # instructions
            event_urgency = 'low'  # urgency
            event_severity = 'low'  # severity
            headline = f"Vessel encounter alert from {vessel_name}"  # headline

        if event_type.upper() == "GAP":  # AIS Disabled alert
            description = f"AIS transponder disabled for {vessel_name} ({mmsi})"
            instructions = "None"  # instructions
            event_urgency = 'low'  # urgency
            event_severity = 'low'  # severity
            headline = f"AIS Transponder disabled for {vessel_name}"
            event_urgency = 'low'  # urgency
            event_severity = 'low'  # severity
            status = "UNKNOWN"

    """
    Building entity dictionary
    """
    entity.update({'mmsi': mmsi})
    if vessel_name in vessels_operator.attrs.keys() or vessel_name == 'None' or vessel_name == '':
        entity.update({'vessel_name': "UNKNOWN"})
    else:
        entity.update({'vessel_name': vessel_name})
    if callsign == 'None' or callsign == '' or callsign in vessels_operator.attrs.keys():
        entity.update({'callsign': 'UNKNOWN'})
    else:
        entity.update({'callsign': callsign})
    entity.update({'timestamp': timestamp})
    entity.update({'heading': heading})
    entity.update({'speed': speed})
    entity.update({'current_status': status})
    entity.update({'src': src})
    entity.update({'type': vessel_type.upper()})
    if flag == 'None' or flag == '' or flag in vessels_operator.attrs.keys():
        entity.update({'flag': "OTHER"})
    else:
        entity.update({'flag': flag})
    entity.update({'length': 0.0})
    entity.update({'width': 0.0})
    entity.update({'draft': 0.0})
    entity.update({'cargo_weight': 0.0})
    entity.update({'lat': lat})
    entity.update({'lon': lon})
    entity.update({'dist_from_port': dist_from_port})
    entity.update({'dist_from_shore': dist_from_shore})
    entity.update({'geom': dumps({
        'type': "Point",
        'coordinates': [lon, lat],
    })})

    # Entity built! Add to array
    # print("Compiled entity:")
    # pprint(entity)
    vessel_payload.append(entity)

    # input()

"""
I'm using this to add constructed entities to DB, but I imagine this is where
the Kafka stuff will go as well
"""
dubs = 0
failures = []
for yarg in vessel_payload:
    try:
        vessels_operator.add(yarg.copy())
        vessels_operator.commit()
        dubs += 1
    except Exception as e:
        print(f"An error occured adding vessel to DB...\n{e}")
        print("This vessel caused the failure:")
        pprint(yarg)
        input()
        failures.append(yarg)

print(f"{dubs} total pushes to DB.")
print(f"{len(failures)} total vessels that weren't added to DB for some reason")

# TODO: DUNNO IF THE FOLLOWING ACCURATELY SAVES DATA
with open('gfw-vessels-failures.csv', 'w', newline='') as outFile:
    writer = csv.DictWriter(outFile, delimiter=',',
                            fieldnames=failures[0].keys())
    writer.writeheader()
    for goob in failures:
        writer.writerow(goob)





















