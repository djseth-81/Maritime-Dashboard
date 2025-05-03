import sys
import requests
import csv
from pprint import pprint
from datetime import datetime, timezone
from time import sleep
from ...DBOperator import DBOperator
from kafka import KafkaProducer
from backend.kafka_service.producer import send_message
from json import dumps

"""
// TODO
- Convert types to coincide with DB
- VERIFY DATA KEYS AND UNITS ARE WHAT I THINK THEY ARE
- improve logging, error handling
"""

TOPIC = 'COOP'
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: str(k).encode('utf-8')
)

def fetch_station_datums(station_id: str) -> list[str]:
    """MDAPI call to get available datums for a station."""
    url = (
        f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
        f"stations/{station_id}/datums.json"
    )
    r = requests.get(url)
    if r.status_code != 200:
        return []
    return [d.get('product') for d in r.json().get('datums', [])]

def request_data(station_id: str, product: str):
    """Hit the DataGetter endpoint; return JSON or raw Response on error."""
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
    now   = datetime.now(timezone.utc)
    ts_iso = now.isoformat()
    ts_int = int(now.timestamp())

    sources_db = DBOperator(table='sources')
    stations   = sources_db.query([{'type': 'NOAA-COOP'}])
    sources_db.close()
    print(f"Fetched {len(stations)} stations from DB")
    if not stations:
        print("No stations found. Exiting.")
        sys.exit(0)

    all_datums  = (
        "water_temperature conductivity salinity water_level hourly_height "
        "high_low daily_mean monthly_mean one_minute_water_level predictions "
        "air_gap currents currents_predictions ofs_water_level"
    ).split()
    recordables = {"water_temperature", "water_level", "wave_height", "conductivity", "salinity"}

    oce_db = DBOperator(table='oceanography')
    ocean_reports = []
    failures = []

    for st in stations:
        sid       = st['id']
        available = st.get('datums')
        if len(available) < 1:
            print(f"Station {sid} does not report data.")
            continue

        report = {
            'src_id':   sid,
            'timestamp': ts_iso,
        }

        for key in recordables:
            if key not in available:
                continue

            data = request_data(sid, key)
            if isinstance(data, requests.Response) and data.status_code >= 400:
                print(f"HTTP ERROR {data.status_code} for {key} @ {sid}")
                break
            if isinstance(data, dict) and data.get('error'):
                continue

            entry = data['data'][0]
            val   = entry.get('s') if key == 'salinity' else entry.get('v')
            report[key] = val

        try:
            oce_db.add(report.copy())
            oce_db.commit()
        except Exception as e:
            oce_db.rollback()
            print(f"WARNING: Failed to add Oceanography report to DB:\n")
            print("This report failed:")
            pprint(report)
            input()
            failures.append(report)

        print(f"Kafka: Sending ocean report for station {sid}")
        producer.send(TOPIC, key=sid, value=report)

        ocean_reports.append(report)
        sleep(0.1)

    producer.flush()
    producer.close()

    oce_db.close()

    if failures:
        with open('coop-oce-failures.csv','a',newline='') as f:
            w = csv.DictWriter(f, fieldnames=failures[0].keys())
            w.writeheader()
            w.writerows(failures)
        print(f"Wrote {len(failures)} failures to coop-oce-failures.csv")

if __name__ == '__main__':
    main()
