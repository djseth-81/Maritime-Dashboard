import csv
import requests
from datetime import datetime, timedelta
from pprint import pprint
from time import sleep
from ...DBOperator import DBOperator

"""
// Thinkin' Thoughts
- I wonder if it's worth it to combine this and the NWS Forecast API into one
  that pulls stations based on Within() Zone, so Missing data can be
  potentially accounted between one another

// TODO
- Convert types to coincide with DB
- VERIFY DATA KEYS AND UNITS ARE WHAT I THINK THEY ARE
- Test
    - improve logging
    - error handling
    - Adding/modifying DB entries
- IDK what the following mean:
    - OFS Water leve
    - Predictions
    - Keys in some of the entries
"""


def request(id, product):
    res = requests.get(
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={id}&product={product}&datum=STND&time_zone=gmt&units=english&format=json")
    # print(f"Status: {res.status_code}")
    if res.status_code >= 400:
        return res
    return res.json()


ocean_reports = []
notices = []

sources = DBOperator(table='sources')
oce = DBOperator(table='oceanography')

stations = sources.query([{'type': 'NOAA-COOP'}])

# All known oceanographic datums
datums = "water_temperature conductivity salinity water_level hourly_height high_low daily_mean monthly_mean one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level".split()

# Oceanographic data we're currently recording
things = "water_temperature conductivity salinity water_level".split()

# Get current time
timestamp = datetime.now()

# iterate through stations
for station in stations:
    ocean_report = {
        # TODO: remove geom, region, lat, lon
        # TODO: Rename to water_temperature
    }

    # Metadata for ocean_report
    # print(f"# Station {station['name']} ({station['id']})")
    ocean_report.update({'src_id': station['id']})
    # print(f"timestamp: {timestamp.strftime('%Y-%m-%dT%H:%M:%S')}")
    ocean_report.update({'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S')})

    # Iterates through expected datums, and sees if station reports it. If so,
    # report
    for thing in datums:
        # If expected datum is not recorded by station, continue
        if thing not in station['datums']:
            # print(f"No {thing} to report from {station['name']}")
            if thing in things:  # if we care about datum, record
                # datum is entered as null
                ocean_report.update({f'{thing}': None})
            continue

        # Executes API call to pull datum
        data = request(station['id'], thing)

        # If client or server error, quit while we're ahead and print out returned error
        if type(data) is not type({"1": 1}) and data.status_code >= 400:
            print("### COOP-Oceanography API: HTTP ERROR:")
            pprint(data.json())
            break

        # if error found in data keys when trying a datum, notify that it's no longer valid
        if 'error' in data.keys():
            # TODO: Enable modify() to update datums for station
            print(
                f"### Meteorology API: {thing} expected, but is no longer recorded at station {station['name']} ({station['id']})")
            if thing in things:  # if we care about datum, record entry
                # datum is entered as null
                ocean_report.update({f'{thing}': None})
            continue

        # The JSON for salinity datums is structured differently than the others...
        if thing == "salinity":
            # is this even the datapoint to collect?
            ocean_report.update({f'{thing}': data['data'][0]['s']})
        elif thing in things:  # If data is currently in list of datums to record, record.
            ocean_report.update({f'{thing}': data['data'][0]['v']})
        # else: # otherwise, just print to console. Might be worth looking @ later
            # print(f"{thing} report from {station['name']}:")
            # pprint(data)

    ocean_reports.append(ocean_report)

    sleep(0.1)  # to avoid 504 Gateway Timeout

print(f'{len(ocean_reports)} oceanography reports to push to DB')

failures = []
for entity in ocean_reports:
    try:
        """
        I'm using this to add constructed entities to DB, but I imagine this is
        where the Kafka stuff will go as well
        """
        print("Adding oceanography report to Oceanography...")
        # Adding event TODO!
        # events_operator.add(entity.copy())
        # events_operator.commit()

        # Updating related vessel TODO!
        # vessels_operator.modify(entity.copy()) # TODO: TEST!
        # vessels_operator.commit()
    except Exception as e:
        print(f"An error occured adding oceanography report to DB...\n{e}")
        print("This report caused the failure:")
        pprint(entity)
        input()
        failures.append(entity)

if len(failures) > 0:
    with open('coop-oce-failures.csv', 'w', newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',',
                                fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)

# DATUMS URL
# datums_url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station[id]}/datums.json"
