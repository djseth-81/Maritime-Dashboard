
import pytz
import os
import sys
import requests
from pprint import pprint
from json import dumps
from datetime import datetime, timedelta
from ...DBOperator import DBOperator
from kafka import KafkaProducer

def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    return response.json()

GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
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
    ]
}

vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

date = datetime.now()
utc = pytz.UTC
vessel_payload = []

vessels_url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search?query=mmsi&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
vessels = query(vessels_url)

entries = vessels['entries']

for entry in entries:
    entity = {}

    index = 0
    diff = date.year
    for i, item in enumerate(entry['combinedSourcesInfo']):
        if (date.year - item['shiptypes'][0]['yearTo']) < diff:
            diff = date.year - item['shiptypes'][0]['yearTo']
            index = i

    vessel_type = entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']

    index = 0
    diff = timedelta(days=date.year)
    for i, item in enumerate(entry['selfReportedInfo']):
        startDate = datetime.fromisoformat(item['transmissionDateFrom'])
        endDate = datetime.fromisoformat(item['transmissionDateTo'])
        if (utc.localize(date) - endDate <= diff):
            diff = endDate - utc.localize(date)
            index = i

    callsign = entry['selfReportedInfo'][index]['callsign']
    flag = entry['selfReportedInfo'][index]['flag']
    vessel_name = entry['selfReportedInfo'][index]['shipname']
    src = f"GFW-{entry['selfReportedInfo'][index]['sourceCode'][0]}"
    mmsi = entry['selfReportedInfo'][index]['ssvid']
    startDate = datetime.fromisoformat(entry['selfReportedInfo'][index]['transmissionDateFrom'])
    endDate = datetime.fromisoformat(entry['selfReportedInfo'][index]['transmissionDateTo'])
    timestamp = entry['selfReportedInfo'][index]['transmissionDateTo'] if (utc.localize(date) > endDate) else entry['selfReportedInfo'][index]['transmissionDateFrom']

    data.update({"vessels": [entry['selfReportedInfo'][index]['id']]})
    events_url = f"https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
    events = requests.post(events_url, headers=headers, json=data)
    if events.status_code >= 400:
        continue

    events_data = events.json()['entries']
    if len(events_data) == 0:
        continue

    index = 0
    diff = timedelta(days=date.year)
    for i, event in enumerate(events_data):
        endDate = datetime.fromisoformat(event['end'])
        if (utc.localize(date) - endDate <= diff):
            diff = endDate - utc.localize(date)
            index = i

    event = events_data[index]

    lat = event['position']['lat']
    lon = event['position']['lon']
    event_type = event['type']

    status = "UNKNOWN"
    if event_type.upper() == 'FISHING':
        speed = event[event_type]['averageSpeedKnots']
        status = 'FISHING'
    elif event_type.upper() == 'LOITERING':
        speed = event[event_type]['averageSpeedKnots']
        status = 'LOITERING' if speed == 0 else 'LIMITED MOVEMENT'
    elif event_type.upper() == 'PORT_VISIT':
        speed = 0
        status = 'ANCHORED'
    elif event_type.upper() == 'GAP':
        speed = 0
        status = 'UNKNOWN'
    else:
        speed = 0

    dist_from_port = event['distances'].get('endDistanceFromPortKm', 0)
    dist_from_shore = event['distances'].get('endDistanceFromShoreKm', 0)

    entity.update({
        'mmsi': mmsi,
        'vessel_name': vessel_name or 'UNKNOWN',
        'callsign': callsign or 'UNKNOWN',
        'timestamp': timestamp,
        'heading': 0,
        'speed': speed,
        'current_status': status,
        'src': src,
        'type': vessel_type.upper(),
        'flag': flag or "OTHER",
        'length': 0.0,
        'width': 0.0,
        'draft': 0.0,
        'cargo_weight': 0.0,
        'lat': lat,
        'lon': lon,
        'dist_from_port': dist_from_port,
        'dist_from_shore': dist_from_shore,
        'geom': dumps({'type': "Point", 'coordinates': [lon, lat]}),
    })

    producer.send("maritime-vessels", key=mmsi, value=entity)
    print(f"Kafka: Sent vessel info for {mmsi}")

producer.flush()

