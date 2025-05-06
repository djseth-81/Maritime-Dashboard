import os
import sys
import requests
from pprint import pprint
from json import dumps
from ...DBOperator import DBOperator
from datetime import datetime, timedelta
import pytz
from kafka import KafkaProducer

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

# GFW Auth
GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
    sys.exit("No GFW API Token provided.")

# DB setup
vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

# Time setup
now = datetime.now()
utc = pytz.UTC

# Headers & API Payload
headers = { "Authorization": f"Bearer {GFW_TOKEN}" }
data = {
    "datasets": ["public-global-port-visits-events:latest"],
    # "startDate": "2025-01-01",
    "startDate": (now - timedelta(weeks=1)).strftime("%Y-%m-%d"),
    "endDate": now.strftime("%Y-%m-%d"),
}

# Fetch events
events_url = "https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
response = requests.post(events_url, headers=headers, json=data)
print("Status Code:", response.status_code)

if response.status_code not in [200, 201]:
    print("Failed to fetch port visit events.")
    print(response.text)
    sys.exit()

events_data = response.json().get("entries", [])

# Initializing DBOperators for Vessels, Events, and Archive
VesselsOp = DBOperator(table = "vessels")
types = VesselsOp.fetch_filter_options()['types']
ArchiveOp = DBOperator(table = "vessel_archive")
EventsOp = DBOperator(table='events')

for event in events_data:
    try:
        """
        Compile event details and push to Topic
        """
        event_type = event['type']
        vessel = event.get("vessel", {})
        vessel_name = vessel.get("name", "UNKNOWN")
        mmsi = vessel.get("ssvid", None)
        if mmsi is None:
            print("Vessel has unidentafiable MMSI")
            continue

        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])
        timestamp = event["end"] if utc.localize(now) > end else event["start"]

        # Description & metadata
        alert = {
            "src_id": mmsi,
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "effective": event["start"],
            "end_time": event["end"],
            "active": start <= utc.localize(now) < end,
            "type": event_type.upper(),
            "description": f"{vessel_name} ({mmsi}) is visiting port",
            "expires": event["end"],
            "instructions": "None",
            "urgency": "low",
            "severity": "low",
            "headline": f"{vessel_name} port visit detected",
        }

        # Send to Kafka
        producer.send("Events", key=mmsi, value=alert)
        print(f"Kafka: Sent port visit event for vessel {mmsi}")
        EventsOp.add(alert.copy()) # Save port visit to Events table
        EventsOp.commit()

        """
        Update vessel status, save to DB, and push to Topic
        """
        speed = float(event[event_type].get("averageSpeedKnots", 0.0))
        lat = float(event['position'].get('lat',0.0))
        lon = float(event['position'].get('lon',0.0))
        geom = {'type': "Point",
                 'coordinates': [lon, lat],
                 }

        if alert['active']:
            status = event_type.upper()
            dist_port = float(event['distances'].get('startDistanceFromPortKm'))
            dist_shore = float(event['distances'].get('startDistanceFromShoreKm'))
        elif utc.localize(now) >= end:
            status = "UNKNOWN"
            dist_port = float(event['distances'].get('endDistanceFromPortKm'))
            dist_shore = float(event['distances'].get('endDistanceFromShoreKm'))

        # Try to pull vessel to update
        known_ship = VesselsOp.query([{'mmsi': int(mmsi)}])
        if known_ship: # Vessel exists, let's update it
            print(f"{vessel_name} found!")

            entity = {
                'timestamp': now.strftime("%Y-%m-%dT%H:%M:%S"),
                'speed': speed,
                'current_status': status,
                'lat': lat,
                'lon': lon,
                'geom': geom,
                'dist_from_port': dist_port,
                'dist_from_shore': dist_shore,
            }

            ArchiveOp.add(known_ship[0].copy())
            ArchiveOp.commit()

            VesselsOp.modify({'mmsi': int(mmsi)},entity)
            VesselsOp.commit()
            entity = known_ship[0].update(entity)

        else: # Vessel doesn't exist, so let's add it
            print(f"{vessel_name} Not found in DB")
            entity = {}

            url = f"https://gateway.api.globalfishingwatch.org/v3/vessels/search?query={vessel['id']}&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
            res = requests.get(url,headers=headers)
            if res.status_code not in [200,201]:
                print("Failed to fetch vessel")
                print(response.text)
                sys.exit()
            entry = res.json().get('entries',[])[0]

            # Getting most recent combined data
            index = 0
            diff = now.year
            for i, item in enumerate(entry['combinedSourcesInfo']):
                if (now.year - item['shiptypes'][0]['yearTo']) < diff:
                    diff = now.year - item['shiptypes'][0]['yearTo']
                    index = i
            if entry['combinedSourcesInfo'][index]['shiptypes'][0]['name'] in types:
                entity.update({'type' : entry['combinedSourcesInfo'][index]['shiptypes'][0]['name']})
            else:
                entity.update({'type': "OTHER"})

            # Obtaining most recent self-reported data
            index = 0
            diff = timedelta(days=now.year)
            for i, item in enumerate(entry['selfReportedInfo']):
                startDate = datetime.fromisoformat(item['transmissionDateFrom'])
                endDate = datetime.fromisoformat(item['transmissionDateTo'])
                if (utc.localize(now) - endDate <= diff):
                    diff = endDate - utc.localize(now)
                    index = i

            entity.update({
                'vessel_name': vessel_name,
                'mmsi': int(mmsi),
                'flag': vessel.get('flag','OTHER'),
                'callsign': entry['selfReportedInfo'][index]['callsign'] if not None else "NONE",
                'src' : f"GFW-{entry['selfReportedInfo'][index]['sourceCode'][0]}",
                # Data expected to change with report
                'timestamp' : now.strftime("%Y-%m-%dT%H:%M:%S"),
                'speed': speed,
                'current_status': status,
                'lat': lat,
                'lon': lon,
                'geom': geom,
                'dist_from_port': dist_port,
                'dist_from_shore': dist_shore,
            })

            VesselsOp.add(entity.copy())
            VesselsOp.commit()

        producer.send("Vessels", key=mmsi,value=entity)
        print(f"Kafka: Sent vessel info for {mmsi}")

    except TypeError as e:
        print(f"Error manipulating data:\n{e}")
    except Exception as e:
        print(f"Error processing event {event.get('id')}: {e}")

producer.flush()
