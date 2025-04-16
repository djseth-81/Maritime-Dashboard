import os
import sys
import requests
from pprint import pprint
from json import dumps
from ...DBOperator import DBOperator
from datetime import datetime
import pytz
from kafka import KafkaProducer

# Kafka Producer Setup
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

# Get GFW Token
GFW_TOKEN = os.environ.get("TOKEN")
if not GFW_TOKEN:
    sys.exit("No GFW API Token provided.")

# DB setup
vessels_operator = DBOperator(table='vessels')
events_operator = DBOperator(table='events')

now = datetime.now()
utc = pytz.UTC

# Headers & API Payload
headers = {"Authorization": f"Bearer {GFW_TOKEN}"}
data = {
    "datasets": ["public-global-fishing-events:latest"],
    "startDate": "2024-01-01",
    "endDate": now.strftime("%Y-%m-%d"),
}

# Fetch events
events_url = "https://gateway.api.globalfishingwatch.org/v3/events?offset=0&limit=500"
response = requests.post(events_url, headers=headers, json=data)
print("Status Code:", response.status_code)

if response.status_code not in [200, 201]:
    print("Failed to fetch fishing events.")
    print(response.text)
    sys.exit()

events_data = response.json().get("entries", [])

for event in events_data:
    try:
        event_type = event["type"]
        vessel = event.get("vessel", {})
        vessel_name = vessel.get("name", "Unknown")
        mmsi = vessel.get("mmsi") or vessel.get("ssvid", "Unknown")

        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])
        timestamp = event["end"] if utc.localize(now) > end else event["start"]

        speed = event[event_type].get("averageSpeedKnots", 0)

        entity = {
            "id": event["id"],
            "src_id": mmsi,
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
            "effective": event["start"],
            "end_time": event["end"],
            "active": start <= utc.localize(now) < end,
            "type": event_type.upper(),
            "description": f"{vessel_name} ({mmsi}) reported fishing activity",
            "expires": event["end"],
            "instructions": "None",
            "urgency": "low",
            "severity": "low",
            "headline": f"{vessel_name} fishing event"
        }

        producer.send("maritime-events", key=mmsi, value=entity)
        print(f"Kafka: Sent fishing event for vessel {mmsi}")

    except Exception as e:
        print(f"Error processing event {event.get('id')}: {e}")

producer.flush()
