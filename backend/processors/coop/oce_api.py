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

# Kafka setup
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

    # 1) get NOAA-COOP station list from DB
    sources_db = DBOperator(table='sources')
    stations   = sources_db.query([{'type': 'NOAA-COOP'}])
    pprint(f"Fetched {len(stations)} stations → {[s['id'] for s in stations]}")
    if not stations:
        pprint("⚠️ No stations found. Exiting.")
        sources_db.close()
        sys.exit(0)

    all_datums  = (
        "water_temperature conductivity salinity water_level hourly_height "
        "high_low daily_mean monthly_mean one_minute_water_level predictions "
        "air_gap currents currents_predictions ofs_water_level"
    ).split()
    recordables = {"water_temperature", "water_level"}

    ocean_reports = []

    # 2) build & send
    for st in stations:
        sid       = st['id']
        available = st.get('datums') or fetch_station_datums(sid)

        report = {
            'src_id':   sid,
            'timestamp': ts_iso,
            'type':     'ocean_report'
        }

        for key in all_datums:
            if key not in available:
                if key in recordables:
                    report[key] = None
                continue

            data = request_data(sid, key)
            if isinstance(data, requests.Response) and data.status_code >= 400:
                pprint(f"HTTP ERROR {data.status_code} for {key} @ {sid}")
                break
            if isinstance(data, dict) and data.get('error'):
                if key in recordables:
                    report[key] = None
                continue

            entry = data['data'][0]
            val   = entry.get('s') if key == 'salinity' else entry.get('v')
            if key in recordables:
                report[key] = val

        # 3) publish to Kafka
        pprint(f"Kafka: Sending ocean report for station {sid}")
        producer.send(TOPIC, key=sid, value=report)

        ocean_reports.append(report)
        sleep(0.1)

    producer.flush()
    producer.close()

    # 4) persist to Postgres
    oce_db  = DBOperator(table='oceanography')
    failures = []
    for rpt in ocean_reports:
        try:
            db_entry = {
                'src_id':     rpt['src_id'],
                'timestamp':  ts_int,
                'water_temp': rpt.get('water_temperature'),
                'wave_height': rpt.get('water_level')
            }
            oce_db.add(db_entry)
            oce_db.commit()
        except Exception as e:
            oce_db.rollback()
            failures.append(rpt)
    oce_db.close()
    sources_db.close()

    if failures:
        with open('coop-oce-failures.csv','w',newline='') as f:
            w = csv.DictWriter(f, fieldnames=failures[0].keys())
            w.writeheader()
            w.writerows(failures)
        pprint(f"Wrote {len(failures)} failures to coop-oce-failures.csv")

if __name__ == '__main__':
    main()