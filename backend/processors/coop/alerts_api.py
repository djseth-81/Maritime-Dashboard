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

    EventsOp = DBOperator(table='events')

    failures = []

    for st in stations:
        sid = st['id']
        name = st.get('name','')

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
                    'type':      'OCE-NOTICE',
                    'description': n0.get('text'),
                    'expires':    (ts + timedelta(hours=1)).isoformat(),
                    'instructions': 'None',
                    'urgency':     'low',
                    'severity':    'low',
                    'headline':    n0.get('name')
                }

                try:
                    EventsOp.add(notice.copy())
                    EventsOp.commit()
                except Exception as e:
                    EventsOp.rollback()
                    print(f"WARNING: Failure to save Marine notice to DB:\n{e}")
                    print("This report failed:")
                    pprint(notice)
                    failures.append(notice)

                print(f"Kafka: Sending notice for station {sid}")
                producer.send('Events', key=sid, value=notice)

        sleep(0.1)

    producer.flush()
    producer.close()
    EventsOp.close()

    if failures:
        with open('coop-notice-failures.csv','a',newline='') as f:
            w = csv.DictWriter(f, fieldnames=failures[0].keys())
            w.writeheader()
            w.writerows(failures)
        print(f"Wrote {len(failures)} failures to coop-oce-failures.csv")

if __name__ == "__main__":
    main()
