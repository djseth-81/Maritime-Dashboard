import os
import sys
import requests
from pprint import pprint
from json import dumps
from ...DBOperator import DBOperator
from datetime import datetime
import pytz
from kafka import KafkaProducer

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

# Get GFW token
GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
    sys.exit("No GFW API Token provided.")

# Set up DB handlers
vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

# Time config
now = datetime.now()
utc = pytz.UTC

# API headers and payload
headers = {"Authorization": f"Bearer {GFW_TOKEN}"}
data = {
    "datasets": ["public-global-loitering-events:latest"],
    "startDate": "2024-01-01",
    "endDate": now.strftime("%Y-%m-%d"),
}

# Fetch events
# Fetch events
events_url = "https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
response = requests.post(events_url, headers=headers, json=data)
print("Status Code:", response.status_code)

if response.status_code not in [200, 201]:
    print("Response content:")
    print(response.text)
    sys.exit("Failed to fetch events.")

payload = response.json()
events_data = payload.get("entries", [])


for event in events_data:
    try:
        event_type = event['type']
        vessel = event.get("vessel", {})
        vessel_name = vessel.get("name", "Unknown")
        mmsi = vessel.get("mmsi") or vessel.get("ssvid", "Unknown")

        # Parse timing
        start = datetime.fromisoformat(event['start'])
        end = datetime.fromisoformat(event['end'])
        timestamp = event['end'] if utc.localize(now) > end else event['start']

        # Determine vessel status
        speed = event[event_type].get('averageSpeedKnots', 0)
        status = 'LOITERING' if speed == 0 else 'LIMITED MOVEMENT'

        # Coordinates
        lat = event['position']['lat']
        lon = event['position']['lon']
        dist_from_port = event['distances'].get('endDistanceFromPortKm')
        dist_from_shore = event['distances'].get('endDistanceFromShoreKm')

        entity = {
            "id": event['id'],
            "src_id": mmsi,
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "effective": event['start'],
            "end_time": event['end'],
            "active": start <= utc.localize(now) < end,
            "type": event_type.upper(),
            "description": f"{vessel_name} ({mmsi}) has been reported loitering",
            "expires": event['end'],
            "instructions": "None",
            "urgency": "low",
            "severity": "low",
            "headline": f"{vessel_name} found loitering"
        }

        # Send to Kafka
        producer.send("maritime-events", key=mmsi, value=entity)
        print(f"Kafka: Sent event for vessel {mmsi}")

    except Exception as e:
        print(f"Error processing event {event.get('id')}: {e}")

producer.flush()
