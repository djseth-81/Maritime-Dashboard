import os
import sys
import requests
from pprint import pprint
from json import dumps
from ...DBOperator import DBOperator
from datetime import datetime, timedelta
import pytz
from kafka import KafkaProducer
from psycopg2.errors import *

# Kafka producer setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

# Token check
GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
    sys.exit("No GFW API Token provided.")

# DB Operators
vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

now = datetime.now()
utc = pytz.UTC

# Headers & API Payload
headers = {"Authorization": f"Bearer {GFW_TOKEN}"}
data = {
    "datasets": ["public-global-gaps-events:latest"],
    # "startDate": "2025-01-01",
    "startDate": (now - timedelta(weeks=1)).strftime("%Y-%m-%d"),
    "endDate": now.strftime("%Y-%m-%d"),
}

# API call
events_url = "https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
response = requests.post(events_url, headers=headers, json=data)
if response.status_code >= 400:
    print("Failed to fetch transponder events.")
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
        event_type = event["type"]
        vessel = event.get("vessel", {})
        vessel_name = vessel.get("name", "UNKNOWN")
        mmsi = vessel.get("ssvid", None)
        if mmsi is None:
            print("Vessel has unidentafiable MMSI")
            continue

        if vessel_name in VesselsOp.attrs or vessel_name is None:
            vessel_name = "UNKNOWN"

        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])
        if end < utc.localize((now - timedelta(days=365))):
            print("Event over a year old. Ignoring")
            continue
        timestamp = event["end"] if utc.localize(now) > end else event["start"]

        alert = {
            "event_id": event['id'],
            "src_id": mmsi,
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "effective": event["start"],
            "end_time": event["end"],
            "active": start <= utc.localize(now) < end,
            "type": event_type.upper(),
            "description": f"{vessel_name} ({mmsi}) AIS transponder gap detected",
            "expires": event["end"],
            "instructions": "None",
            "urgency": "low",
            "severity": "low",
            "headline": f"AIS Transponder gap for {vessel_name}"
        }

        EventsOp.add(alert.copy()) # Save port visit to Events table
        EventsOp.commit()
        # Send to Kafka
        producer.send("Events", key=mmsi, value=alert)
        print(f"Kafka: Sent port visit event for vessel {mmsi}")

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

            for key,value in entity.copy().items():
                if value == known_ship[0][key]:
                    entity.pop(key)

            guh = entity.copy()
            guh.pop('timestamp','')
            if len(guh) > 0:
                # Archiving old Vessel state
                ArchiveOp.add(known_ship[0].copy())
                ArchiveOp.commit()

                # Updating vessel in DB
                VesselsOp.modify({'mmsi': int(mmsi)},entity)
                VesselsOp.commit()
                entity = known_ship[0].update(entity)

                # Pishing to Kafka
                producer.send("Vessels", key=mmsi,value=entity)
                print(f"Kafka: Sent vessel info for {mmsi}")

        else: # If transponder isn't active, of course it wouldn't be found
            print(f"{vessel_name} not recognized. Ignoring.")
            continue

    except TypeError as e:
        print(f"Error manipulating data:\n{e}")
        VesselsOp.rollback()
        ArchiveOp.rollback()
        EventsOp.rollback()
    except UniqueViolation as e:
        VesselsOp.rollback()
        ArchiveOp.rollback()
        EventsOp.rollback()
        print(f"{e}\nEntity already exists in DB. Ingoring.")
    except Exception as e:
        print(f"Error processing event {event.get('id')}: {e}")
        VesselsOp.rollback()
        ArchiveOp.rollback()
        EventsOp.rollback()

producer.flush()
