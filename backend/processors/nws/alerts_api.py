import csv
import pytz
import os
import sys
import requests
from pprint import pprint
from datetime import datetime
from json import dumps
from ...DBOperator import DBOperator
from kafka import KafkaProducer

"""
NOAA NWS Alerts API
- Currently uses Zone ID to pull relevant active zones, but would be cool to
  search by station
    - OR I can implement the station.within(zone)
    - OR zone.contain(station_id)
    TRY BOTH

"""
now = datetime.now()
utc = pytz.UTC

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

def nws_alerts(zone: dict):

    alerts_url = f"https://api.weather.gov/alerts?zone={zone['id']}"
    res = requests.get(alerts_url)
    if res.status_code not in [200, 201]:
        print(f"Error retrieving alerts from {zone['id']}:\n{res.text}")
        return None

    # Pagination which I think would be helpful. Sometime in the future
    # pagination_url = res.json()['pagination']['next']
    # print(f"Pagination URI: {pagination_url}") if pagination_url else print()
    # print(f"Number of alerts retrieved: {len(res.json()['features'])}\n")

    # For the sake of not bloating tf out of the events processed, we're just
    # gonna start with the most recent one. IT'S PURELY A GUESS that the first
    # element in the payload array is the most recent

    if len(res.json()['features']) < 1:
        print(f"{zone['id']} has no events to report.")
        return None

    alert = res.json()['features'][0]
    # pprint(alert['properties'])
    # input()

    # Might be good if we wanna store quick references to alerts later
    # print("Onset time:")
    # pprint(alert['properties']['onset'])

    # print("Replacement time:")
    # pprint(alert['properties']['replacedAt']) if 'replacedAt' in alert['properties'].keys(
    # ) else print("Nothing to replace")

    # # ID to check upon expiration, if exists. Otherwise, just broadly query
    # print("Replaced by URI:")
    # if 'replacedBy' in alert['properties'].keys():
    #     pprint(alert['properties']['replacedBy'])
    #     print("AlertID replacing this one:")
    #     pprint(alert['properties']['replacedBy'].split(':')[-1])
    # else:
    #     print("Nothing to replace")
    # print()

    # GFW Vessel Events also apparently reports some "region", so it might be
    # cool to store this if we wanna in the future...
    # print("Affected Zones:")
    # pprint(alert['properties']['geocode']['UGC'])
    # pprint(alert['properties']['areaDesc'])
    # print()

    # should I juststore this in events.description?
    # print("Certainty:")
    # pprint(alert['properties']['certainty'])
    # print()

    return {
        "timestamp": alert['properties']['sent'],
        "effective": alert['properties']['effective'],
        "end_time": alert['properties']['ends'],
        "active": datetime.fromisoformat(alert['properties']['effective']) <= utc.localize(now) < datetime.fromisoformat(alert['properties']['expires']),
        "type": f"{alert['properties']['category'].upper()}-{alert['properties']['messageType'].upper()}",
        "description": alert['properties']['description'],
        "expires": alert['properties']['expires'],
        "instructions": alert['properties']['instruction'],
        "urgency": alert['properties']['urgency'],
        "severity": alert['properties']['severity'],
        "headline": alert['properties']['headline'],
    }

def main():
    StationOp = DBOperator(table='sources')
    stations = StationOp.query([{'type': 'NOAA-NWS'}])
    StationOp.close()
    ZoneOp = DBOperator(table='zones')
    EventsOp = DBOperator(table='events')

    for station in stations:
        entity = {}
        zones = ZoneOp.query([{'src_id': station['id']}])
        for zone in zones:
            if zone['type'] == 'COUNTY':
                guh = nws_alerts(zone)
                if guh is not None:
                    entity.update({'src_id': station['id']})
                    entity.update(guh)

                    try:
                        producer.send("Events", key=station['id'], value=entity)
                        print(f"Kafka: Sent alert for station {station['id']}")
                        EventsOp.add(entity.copy())
                        EventsOp.commit()
                    except Exception as e:
                        print(f"Failed to send alert for {station['id']}: {e}")
    producer.flush()
    ZoneOp.close()
    EventsOp.close()

if __name__ == "__main__":
    main()

