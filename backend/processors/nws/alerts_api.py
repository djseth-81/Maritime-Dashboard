import csv
import pytz
import requests
from pprint import pprint
from datetime import datetime
from json import loads, dumps
from ...DBOperator import DBOperator

"""
id = Alert ID (??)
src_id ??? <- Reprots Source name, but I'd prefer source CWA
timestamp = sent time
effective = Effective time
end_time = End time
active = '{if effective <= current_time < end_time}'
type = '{Category}-{messageType}'
description = Description
expires = Alert Expiration time
instructions = Instructions
urgency = Urgency
severity = Severity
headline = Headline

NOAA NWS Alerts API
- Currently uses Zone ID to pull relevant active zones, but would be cool to
  search by station
    - OR I can implement the station.within(zone)
    - OR zone.contain(station_id)
    TRY BOTH

"""
now = datetime.now()
utc = pytz.UTC


def nws_alerts(zone: dict):

    alerts_url = f"https://api.weather.gov/alerts?zone={zone['id']}"
    res = requests.get(alerts_url)
    if res.status_code not in [200, 201]:
        print(
            f"Error trying to retrieve alerts from {zone['id']}:\n{res.text}")
        return

    # Pagination which I think would be helpful. Sometime in the future
    # pagination_url = res.json()['pagination']['next']
    # print(f"Pagination URI: {pagination_url}") if pagination_url else print()
    # print(f"Number of alerts retrieved: {len(res.json()['features'])}\n")

    # For the sake of not bloating tf out of the events processed, we're just
    # gonna start with the most recent one. IT'S PURELY A GUESS that the first
    # element in the payload array is the most recent

    if len(res.json()['features']) < 1:
        print(f"{zone['id']} has no events to report.")
        return

    # Checking out bug since alert['properties']['parameters']['NWSheadline'][0]
    # throws an error sometimes
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


if __name__ == "__main__":
    alerts = []
    StationOp = DBOperator(table='sources')
    stations = StationOp.query([{'type': 'NOAA-NWS'}])
    StationOp.close()
    ZoneOp = DBOperator(table='zones')

    for station in stations:
        print(f"Station: {station['id']}")
        entity = {}

        # zones = ZoneOp.contains(loads(station['geom']))
        zones = ZoneOp.query([{'src_id': station['id']}])
        pprint(len(zones))
        for zone in zones:
            if zone['type'] == 'COUNTY':
                print(f"Zone contatining station: {zone['id']}")
                guh = nws_alerts(zone)

        if guh is not None:
            entity.update({'src_id': station['id']})
            entity.update(guh)

        alerts.append(entity)
    ZoneOp.close()

    failures = []
    events = DBOperator(table='events')
    for entity in alerts:
        try:
            print("Adding NWS weather report to met table")
            events.add(entity.copy())
            events.commit()
        except Exception as e:
            print(f"An error occured saving weather report...\n{e}")
            print("This report caused the failure:")
            pprint(entity)
            input()  # DEBUG
            if entity is not None:
                failures.append(entity)
    events.close()

    if len(failures) > 0:
        with open('nws-weather-failures.csv', 'w', newline='') as outFile:
            writer = csv.DictWriter(outFile, delimiter=',',
                                    fieldnames=failures[0].keys())
            writer.writeheader()
            for goob in failures:
                writer.writerow(goob)
