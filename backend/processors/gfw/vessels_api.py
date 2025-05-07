
import pytz
import os
import sys
import requests
from pprint import pprint
from json import dumps
from datetime import datetime, timedelta
from ...DBOperator import DBOperator
from kafka import KafkaProducer

GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
    sys.exit("No GFW API Token provided.")

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

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
    ]
}

# Spawning DB operators
ArchiveOp = DBOperator(table='vessel_archive')
VesselsOp = DBOperator(table='vessels')
types = VesselsOp.fetch_filter_options()['types']

now = datetime.now()
utc = pytz.UTC
vessel_payload = []

vessels_url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search?query=mmsi&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
response = requests.get(vessels_url,headers=headers)
if response.status_code not in [200,201]:
    print("Failed to fetch vessels")
    print(response.text)
    sys.exit()

vessels = response.json().get('entries',[])

for entry in vessels:
    entity = {}

    # Getting most recent combined data
    index = 0
    diff = now.year
    for i, item in enumerate(entry['combinedSourcesInfo']):
        if (now.year - item['shiptypes'][0]['yearTo']) < diff:
            diff = now.year - item['shiptypes'][0]['yearTo']
            index = i

    # If vessel is an acceptable type, save it. Otherwise ignore so it defaults to UNKNOWN
    # if entry['combinedSourcesInfo'][index]['shiptypes'][0]['name'] in types:
    #     entity.update({'type' : entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']})

    # If vessel type is reported, add it
    if entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']:
        entity.update({'type' : entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']})

    # Obtaining most recent self-reported data
    index = 0
    diff = timedelta(days=now.year)
    for i, item in enumerate(entry['selfReportedInfo']):
        startDate = datetime.fromisoformat(item['transmissionDateFrom'])
        endDate = datetime.fromisoformat(item['transmissionDateTo'])
        if (utc.localize(now) - endDate <= diff):
            diff = endDate - utc.localize(now)
            index = i

    startDate = datetime.fromisoformat(entry['selfReportedInfo'][index]['transmissionDateFrom'])
    endDate = datetime.fromisoformat(entry['selfReportedInfo'][index]['transmissionDateTo'])
    if endDate < utc.localize((now - timedelta(days=365))):
        print("Vessel entry is over a year old. Ignoring")
        continue

    # Vessel identifiers
    mmsi = int(entry['selfReportedInfo'][index]['ssvid'])
    vessel_id = entry['selfReportedInfo'][index]['id']

    name = entry['selfReportedInfo'][index]['shipname']
    if name in VesselsOp.attrs or name is None:
        name = "UNKNOWN"

    if entry['selfReportedInfo'][index]['callsign']:
        entity.update({'callsign':entry['selfReportedInfo'][index]['callsign']});
    if entry['selfReportedInfo'][index]['flag']:
        entity.update({'flag':entry['selfReportedInfo'][index]['flag']})

    entity.update({
        'vessel_name' : name,
        'mmsi' : mmsi
    })

    # Reporting details
    entity.update({
        'src' : f"GFW-{entry['selfReportedInfo'][index]['sourceCode'][0]}",
        'timestamp' : entry['selfReportedInfo'][index]['transmissionDateTo'] if (utc.localize(now) > endDate) else entry['selfReportedInfo'][index]['transmissionDateFrom']
    })


    # Fetch events wrt vessel GFW ID
    data.update({"vessels": [entry['selfReportedInfo'][index]['id']]})
    events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
    events = requests.post(events_url, headers=headers, json=data)
    if events.status_code >= 400:
        continue

    events_data = events.json()['entries']
    if len(events_data) == 0:
        continue

    # ... and search for most recent event
    index = 0
    diff = timedelta(days=now.year)
    for i, event in enumerate(events_data):
        endDate = datetime.fromisoformat(event['end'])
        if (utc.localize(now) - endDate <= diff):
            diff = endDate - utc.localize(now)
            index = i
    event = events_data[index]

    end = datetime.fromisoformat(event['end'])
    start = datetime.fromisoformat(event['start'])

    entity.update({
        'lat': event['position']['lat'],
        'lon': event['position']['lon'],
        'geom': {'type': "Point",
                 'coordinates': [event['position']['lon'], event['position']['lat']]
                 }
    })

    event_type = event['type']

    status = "UNKNOWN"
    if event_type.upper() == 'FISHING':
        speed = float(event[event_type]['averageSpeedKnots'])
        status = 'FISHING'
    elif event_type.upper() == 'LOITERING':
        speed = float(event[event_type]['averageSpeedKnots'])
        status = 'LOITERING' if speed == 0.0 else 'LIMITED MOVEMENT'
    elif event_type.upper() == 'PORT_VISIT':
        speed = 0.0
        status = 'ANCHORED'
    elif event_type.upper() == 'GAP':
        speed = 0.0
    else:
        speed = 0.0

    entity.update({
        'current_status' : status,
        'speed' : speed
    })

    if start <= utc.localize(now) < end:
        entity.update({
            'dist_from_port': float(event['distances'].get('startDistanceFromPortKm', 0)),
            'dist_from_shore': float(event['distances'].get('startDistanceFromShoreKm', 0))
        })

    elif end <= utc.localize(now):
        entity.update({
            'dist_from_port': float(event['distances'].get('endDistanceFromPortKm', 0)),
            'dist_from_shore': float(event['distances'].get('endDistanceFromShoreKm', 0))
        })

    # Vessel processing
    vessel = VesselsOp.query([{'mmsi':mmsi}])
    if len(vessel) < 1:
        # print(f"### GFW Vessels API: New vessel identified: {entity['vessel_name']} ({entity['mmsi']}) flying {entity['flag']}")
        # # Adding new vessels to DB
        # VesselsOp.add(entity.copy())
        # VesselsOp.commit()
        # # Update Report info
        # producer.send("Vessels", key=str(mmsi), value=entity.copy())
        # print(f"Kafka: Sent vessel info for {mmsi}")
        print(f"{name} not recognized. Ignoring.")
    else:
        for attr,value in entity.copy().items():
            if value == vessel[0][attr]:
                entity.pop(attr)

        # Using a temp variable to remove timestamp (if any) and see if any OTHER changes have been made
        guh = entity.copy()
        guh.pop('timestamp','')
        # Changes have been made, update vessel data
        if len(guh) > 0:
            # First, archive old vessel state
            try:
                ArchiveOp.add(vessel[0].copy())
                ArchiveOp.commit()

                VesselsOp.modify({'mmsi':vessel[0]['mmsi']},entity.copy())
                VesselsOp.commit()
                vessel[0].update(entity) # Updating local vessel with changes in entity to mirror modification to DB

                # Update Report info
                producer.send("Vessels", key=str(mmsi), value=vessel[0])
                # NOTE: Apparently can encounter a KeyError: 0 for value=vessel[0]?
                #   Keep an eye on this
                print(f"Kafka: Sent vessel info for {mmsi}")
            except Exception as e:
                print(f"Error with processing vessel entry:\n{e}\nThis threw the error:")
                pprint(entity)


VesselsOp.close()
ArchiveOp.close()

producer.flush()


























