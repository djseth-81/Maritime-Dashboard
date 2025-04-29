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
- Test
    - improve logging
    - error handling
    - Adding/modifying DB entries
"""


def request(id, product):
    res = requests.get(
        f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={id}&product={product}&datum=STND&time_zone=gmt&units=english&format=json")
    # print(f"Status: {res.status_code}")
    if res.status_code >= 400:
        return res
    return res.json()


weather_reports = []
notices = []

# Retrieving stations
sources = DBOperator(table='sources')
stations = sources.query([{'type': 'NOAA-COOP'}])


things = "air_temperature wind visibility humidity".split()
timestamp = datetime.now()

# iterate through stations
for station in stations:
    weather_report = {}
    notice = {}

    # Metadata for met weather_report
    # print(f"# Station {station['name']} ({station['id']})")
    # print(f"timestamp: {timestamp.strftime('%Y-%m-%dT%H:%M:%S')}")
    weather_report.update({'src_id': station['id'],
                           'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S')})

    # Iterates through expected datums, and sees if station reports it. If so,
    # report. Otherwise, set as NULL. This is the better outcome, becasue it
    # singles out met data, BUT MORE IMPORTANTLY n will, AT MOST, be 4.
    for thing in things:
        # If expected datum is not recorded by station, continue
        if thing not in station['datums']:
            print(f"No {thing} to report from {station['name']}")
            if thing == 'wind':
                weather_report.update({'wind_heading': None,
                                       'wind_speed': None})
            else:
                weather_report.update({f'{thing}': None})  # datum is entered as null
            continue

        # Executes API call to pull datum
        data = request(station['id'], thing)

        # If client or server error, quit while we're ahead and print out returned error
        if type(data) is not type({"1":1}) and data.status_code not in [200, 201]:
            print(f"### COOP-Meteorology API: HTTP ERROR {data.status_code}")
            # pprint(data.json())
            break

        # if error found in data keys when trying a datum, notify that it's no longer valid
        if 'error' in data.keys():
            # TODO: Enable modify() to update datums for station
            print(f"### COOP-Meteorology API: {thing} expected, but is no longer recorded at station {station['name']} ({station['id']})")
            # I am in a panic for seemingly no reason because I feel like I'm
            # behind for STILL processing API data, so this is just gross
            if thing == 'wind':
                weather_report.update({'wind_heading': None,
                                       'wind_speed': None})
            else:
                weather_report.update({f'{thing}': None})  # datum is entered as null
            continue

        # The JSON for wind datums is structured differently than the others...
        if thing == 'wind':
            # deg?
            # print(f"Wind direction: {data['data'][0]['dr']} ({data['data'][0]['d']})")
            # print(f"Wind speed: {data['data'][0]['s']}")  # kts?
            weather_report.update({'wind_heading': data['data'][0]['d'],
                                   'wind_speed': data['data'][0]['s']})
        else:
            # print(f"{thing}: {data['data'][0]['v']}")  # F/nautical mi/bar?
            weather_report.update({f'{thing}': data['data'][0]['v']})

    weather_report.update({'precipitation': None,
                           'forecast': None,
                           'event_id': None})  # Is this even necessary?
    # pprint(weather_report)
    pprint("### COOP Meteorology API: Queuing weather report...") # Printing for logs
    weather_reports.append(weather_report)

    # Even though I ask if associating weather data to a notice is necessary,
    # I build the notice report anyway
    res = requests.get(
        f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station['id']}/notices.json")
    # print(res.status_code)
    # If a client or server error occurs, quit while we're ahead and print out error
    if res.status_code not in [200,201]:
        print(f"### COOP-Meteorology API: HTTP ERROR {res.status_code}:")
        pprint(res.text)
        break
    data = res.json()
    if len(data['notices']) > 0:
        notice.update({
            'src_id': station['id'],
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            'effective': timestamp.strftime('%Y-%m-%dT%H:%M:%S'),  # Defaulting effective time to when it was discovered
            # Defaulting to the event expiring in an hour from when it was discovered
            'end_time': (timestamp + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),
            'active': True,
            'type': 'Marine alert',
            'description': data['notices'][0]['text'],
            'expires': (timestamp + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S'),  # same as end_time
            'instructions': "None",
            'urgency': "low",
            'severity': "low",
            'headline': data['notices'][0]['name'],
        })
        # pprint(notice)
        pprint("### COOP Meteorology API: Queuing notice...") # Printing for logs
        notices.append(notice)
    input()
    sleep(0.1) # to avoid 504 Gateway Timeout

print(f'{len(weather_reports)} weather reports to push to DB')
print(f'{len(notices)} notices to push to DB')

failures = []

# Adding weather reports
met = DBOperator(table='meteorology')
for entity in weather_reports:
    try:
        """
        I'm using this to add constructed entities to DB, but I imagine this is
        where the Kafka stuff will go as well
        """
        print("Adding weather report to Meteorology...")
        # Adding event
        met.add(entity.copy())
        met.commit()
    except Exception as e:
        print(f"An error occured adding weather report to DB...\n{e}")
        print("This report caused the failure:")
        pprint(entity)
        input() # DEBUG
        failures.append(entity)
met.close()

if len(failures) > 0:
    with open('coop-met-failures.csv', 'w', newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',',
                                fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)

failures = []

# Adding notices reported by stations
events = DBOperator(table='events')
for entity in notices:
    try:
        """
        I'm using this to add constructed entities to DB, but I imagine this is
        where the Kafka stuff will go as well
        """
        print("Adding notice to events table")
        events.add(entity.copy())
        events.commit()
    except Exception as e:
        print(f"An error occured adding notice to DB...\n{e}")
        print("This notice caused the failure:")
        pprint(entity)
        input() # DEBUG
        failures.append(entity)
events.close()

if len(failures) > 0:
    with open('coop-notice-failures.csv', 'w', newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',',
                                fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)


### DATUMS URL
# datums_url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station[id]}/datums.json"





















