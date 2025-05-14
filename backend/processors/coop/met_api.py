import os
import sys
import requests
import csv
from pprint import pprint
from json import dumps
from datetime import datetime, timedelta, timezone
from time import sleep
from ...DBOperator import DBOperator
from kafka import KafkaProducer


"""
// Thinkin' Thoughts
- I wonder if it's worth it to combine this and the NWS Forecast API into one
  that pulls stations based on Within() Zone, so Missing data can be
  potentially accounted between one another
"""


producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: str(k).encode('utf-8')
)

THINGS = ['air_temperature', 'wind', 'visibility', 'humidity']

def fetch_station_datums(station_id: str) -> list[str]:
    """Call the NOAA MDAPI to retrieve the list of available products/datums."""
    url = (
        f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
        f"stations/{station_id}/datums.json"
    )
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Warning: could not fetch datums for {station_id}: HTTP {r.status_code}")
        return []
    return [d.get('product') for d in r.json().get('datums', [])]

def request_data(station_id: str, product: str):
    """Hit the DataGetter endpoint; return JSON or raw response on error."""
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
    ts = datetime.now(timezone.utc)
    ts_iso = ts.isoformat()

    sources_op = DBOperator(table='sources')
    stations = sources_op.query([{'type': 'NOAA-COOP'}])
    sources_op.close()
    print(f"Fetched {len(stations)} stations from DB")

    if not stations:
        print("WARNING: No NOAA-COOP stations found in DB. Exiting.")
        sys.exit(0)

    WeatherOp = DBOperator(table='meteorology')

    failures = []

    for st in stations:
        sid = st['id']
        name = st.get('name','')
        station_datums = st.get('datums')
        if len(station_datums) < 1:
            print(f"Station {sid} does not report data")
            continue
        report = {
            'src_id':   sid,
            'timestamp': ts_iso,
        }

        for aspect in THINGS:
            if aspect not in station_datums:
                continue

            data = request_data(sid, aspect)
            if isinstance(data, requests.Response) and data.status_code >= 400:
                print(f"HTTP ERROR {data.status_code} for {aspect} @ {sid}")
                break
            if isinstance(data, dict) and data.get('error'):
                print(f"{aspect} no longer recorded at {sid}")
                continue

            entry = data['data'][0]
            if aspect == 'wind':
                report.update({'wind_heading': entry.get('d'), 'wind_speed': entry.get('s')})
            else:
                report[aspect] = entry.get('v')


        try:
            WeatherOp.add(report.copy())
            WeatherOp.commit()

        except Exception as e:
            WeatherOp.rollback()
            print(f"WARNING: Failure to save weather report to DB:\n{e}")
            print("This report failed:")
            pprint(report)
            failures.append(report)

        print(f"Kafka: Sending weather report for station {sid}")
        producer.send('Weather', key=sid, value=report)

        sleep(0.1)

    producer.flush()
    producer.close()
    WeatherOp.close()

    if failures:
        with open('coop-met-failures.csv','a',newline='') as f:
            w = csv.DictWriter(f, fieldnames=failures[0].keys())
            w.writeheader()
            w.writerows(failures)
        print(f"Wrote {len(failures)} failures to coop-oce-failures.csv")

if __name__ == "__main__":
    main()
