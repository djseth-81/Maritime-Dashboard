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

// TODO
- Convert types to coincide with DB
- Test
    - improve logging
    - error handling
    - Adding/modifying DB entries
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
        pprint(f"Warning: could not fetch datums for {station_id}: HTTP {r.status_code}")
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
    pprint(f"Fetched {len(stations)} stations from DB")

    if not stations:
        pprint("WARNING: No NOAA-COOP stations found in DB. Exiting.")
        sys.exit(0)

    for st in stations:
        sid = st['id']
        name = st.get('name','')
        station_datums = st.get('datums') or fetch_station_datums(sid)
        report = {
            'src_id':   sid,
            'timestamp': ts_iso,
            'type':     'weather_report'
        }

        for aspect in THINGS:
            if aspect not in station_datums:
                if aspect == 'wind':
                    report.update({'wind_heading': None, 'wind_speed': None})
                else:
                    report[aspect] = None
                continue

            data = request_data(sid, aspect)
            if isinstance(data, requests.Response) and data.status_code >= 400:
                pprint(f"HTTP ERROR {data.status_code} for {aspect} @ {sid}")
                break
            if isinstance(data, dict) and data.get('error'):
                pprint(f"{aspect} no longer recorded at {sid}")
                if aspect == 'wind':
                    report.update({'wind_heading': None, 'wind_speed': None})
                else:
                    report[aspect] = None
                continue

            entry = data['data'][0]
            if aspect == 'wind':
                report.update({'wind_heading': entry.get('d'), 'wind_speed': entry.get('s')})
            else:
                report[aspect] = entry.get('v')

        pprint(f"Kafka: Sending weather report for station {sid}")
        producer.send('COOP', key=sid, value=report)

        notice_url = (
            f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
            f"stations/{sid}/notices.json"
        )
        nr = requests.get(notice_url)
        if nr.status_code in (200,201):
            notices = nr.json().get('notices',[])
            if notices:
                n0 = notices[0]
                notice = {
                    'src_id':   sid,
                    'timestamp': ts_iso,
                    'effective': ts_iso,
                    'end_time':  (ts + timedelta(hours=1)).isoformat(),
                    'active':    True,
                    'type':      'notice',
                    'description': n0.get('text'),
                    'expires':    (ts + timedelta(hours=1)).isoformat(),
                    'instructions': 'None',
                    'urgency':     'low',
                    'severity':    'low',
                    'headline':    n0.get('name')
                }
                pprint(f"Kafka: Sending notice for station {sid}")
                producer.send('COOP', key=sid, value=notice)

        sleep(0.1)

    producer.flush()
    producer.close()
    sources_op.close()

if __name__ == "__main__":
    main()