import sys
import requests
import csv
from pprint import pprint
from datetime import datetime, timezone, timedelta
from time import sleep
from ...DBOperator import DBOperator
from kafka import KafkaProducer
from json import dumps

"""
// Stations ingestion: fetch NOAA CO-OP station metadata,
// publish via Kafka, and persist to Postgres (skipping existing)
"""
# Parsing CO-OP station data of last entry
    # print(f"Name: {station['name']}")
    # print(f"ID: {station['id']}")
    # print(f"State: {station['state']}")
    # print(f"\"shefcode\": {station['shefcode']}")
    # print(f"\"portscode\": {station['portscode']}")
    # print(f"Type: NOAA-{station['affiliations']}")
    # print(f"Timezone: {station['timezone']} (GMT {station['timezonecorr']})")
    # print(f"Lat,Lon: {station['lat']},{station['lng']}")
    # print(f"Disclaimers: {station['disclaimers']['self']}")
    # print(f"Notices: {station['notices']['self']}")
    # print(f"Datums: {station['datums']['self']}")
    # print(f"Forecast: {station['forecast']}")
    # print()

TOPIC = 'COOP'
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: str(k).encode('utf-8')
)

ALL_DATUMS = (
    "air_temperature wind water_temperature air_pressure humidity conductivity visibility "
    "salinity water_level hourly_height high_low daily_mean monthly_mean "
    "one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level"
).split()

def request_dataget(station_id: str, product: str):
    """Return JSON if OK, else raw response for error handling."""
    resp = requests.get(
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
        params={
            'date': 'latest',
            'station': station_id,
            'product': product,
            'datum': 'STND',
            'time_zone': 'gmt',
            'units': 'english',
            'format': 'json'
        }
    )
    return resp if resp.status_code >= 400 else resp.json()

def main():
    ts_iso = datetime.now(timezone.utc).isoformat()

    sources_db = DBOperator(table='sources')

    coop_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    pprint(f"Fetching stations from {coop_url}")
    resp = requests.get(coop_url)
    if resp.status_code != 200:
        pprint(f"ERROR fetching stations: HTTP {resp.status_code}")
        sys.exit(1)
    stations = resp.json().get('stations', [])
    pprint(f"Retrieved {len(stations)} stations")

    inserted = 0
    failures = []

    for st in stations:
        sid = st['id']
        datums = []
        for prod in ALL_DATUMS:
            data = request_dataget(sid, prod)
            if isinstance(data, dict) and data.get('data') and 'error' not in data:
                datums.append(prod)
            sleep(0.05)

        payload = {
            'id':        sid,
            'name':      st.get('name'),
            'region':    st.get('state', 'USA'),
            'type':      'NOAA-COOP',
            'datums':    datums,
            'timezone':  f"{st.get('timezone')} (GMT {st.get('timezonecorr')})",
            'timestamp': ts_iso
        }

        pprint(f"Kafka: Sending station {sid}")
        producer.send(TOPIC, key=sid, value=payload)

        # 3c) skip insert if already exists
        if sources_db.query([{'id': sid}]):
            pprint(f"Skipping DB insert (exists) {sid}")
            continue

        try:
            row = {
                'id':       payload['id'],
                'name':     payload['name'],
                'region':   payload['region'],
                'type':     payload['type'],
                'timezone': payload['timezone'],
                'datums':   payload['datums'],
            }
            sources_db.add(row)
            sources_db.commit()
            inserted += 1
        except Exception as e:
            pprint(f"DB Error inserting station {sid}: {e}")
            sources_db.rollback()
            failures.append(payload)

    producer.flush()
    producer.close()

    total = len(stations)
    pprint(f"Inserted {inserted}/{total} new stations, skipped {total - inserted}")
    if failures:
        fname = 'coop-station-failures.csv'
        with open(fname, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=failures[0].keys())
            w.writeheader()
            w.writerows(failures)
        pprint(f"Wrote {len(failures)} failures to {fname}")

    sources_db.close()

if __name__ == '__main__':
    main()