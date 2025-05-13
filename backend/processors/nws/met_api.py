import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from ...DBOperator import DBOperator

"""
NOAA weather.gov API
- It currently just iterates through NWS stations and uses their own point
    - I *COULD* take the point provided by frontend in here and pull forecast
      THAT WAY for better "accuracy".

There are options that I chose one over the other
- Can do forecastHourly or forecast
    - MORE forecast data, one per hour (duh)
- both provide an array of reports, I just pull the most recent one
    - (all have an "expiration time")

I save...
- the extreme of wind speed, if there is one
- percipitation as a decimal out of 1 (percentage)
- Wind speed as a decimal degree as opposed to cardinal direction

There's more I'm prolly missing
"""

from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)




def nws_weather(station: dict):

    # Get NWS Point
    point_url = f"https://api.weather.gov/points/{station['geom']['coordinates'][1]},{station['geom']['coordinates'][0]}"
    point_report = requests.get(point_url)
    if point_report.status_code not in [200, 201]:
        print(f"Error retrieving point report:\n{point_report.text}")
        return

    # Get NWS forecast
    weather_report = requests.get(
        point_report.json()['properties']['forecast'])
    if weather_report.status_code not in [200, 201]:
        print(f"Error retrieving point report:\n{weather_report.text}")
        return

    report = weather_report.json()

    zone_operator = DBOperator(table='zones')
    zones = zone_operator.contains(report['geometry'])

    timestamp = report['properties']['generatedAt']
    guh = report['properties']['periods'][0]

    # Offensive. Abhorrent. Vile.
    if guh['windDirection'] == "N":
        heading = 0.0
    elif guh['windDirection'] == "NNE":
        heading = 22.5
    elif guh['windDirection'] == "NE":
        heading = 45.0
    elif guh['windDirection'] == "ENE":
        heading = 67.5
    elif guh['windDirection'] == "E":
        heading = 90.0
    elif guh['windDirection'] == "ESE":
        heading = 112.5
    elif guh['windDirection'] == "SE":
        heading = 135.0
    elif guh['windDirection'] == "SSE":
        heading = 157.5
    elif guh['windDirection'] == "S":
        heading = 180.0
    elif guh['windDirection'] == "SSW":
        heading = 202.5
    elif guh['windDirection'] == "SW":
        heading = 225.0
    elif guh['windDirection'] == "WSW":
        heading = 247.5
    elif guh['windDirection'] == "W":
        heading = 270.0
    elif guh['windDirection'] == "WNW":
        heading = 292.5
    elif guh['windDirection'] == "NW":
        heading = 315.0
    elif guh['windDirection'] == "NNW":
        heading = 337.5
    else:
        heading = None # Assume report has no wind to detect
        print("Wind direction is not of the 16 point compass rose", file=sys.stderr)

    # I'm just gonna go ahead and save the high end estimates provided by the report
    index = 0
    for i, item in enumerate(guh['windSpeed'].split()):
        index = i if item.isdigit() else index

    weather_data = {
        'src_id': station['id'],
        'timestamp': timestamp,
        'air_temperature': guh['temperature'],
        'wind_speed': float(guh['windSpeed'].split()[index]),
        'wind_heading': heading,
        'precipitation': (float(guh['probabilityOfPrecipitation']['value']) / 100) if guh['probabilityOfPrecipitation']['value'] is not None else None,
        'humidity': None,
        'forecast': None,
        'event_id': None,
        'visibility': None,
    }

    try:
        producer.send("Weather", key=station['id'], value=weather_data)
        print(f"Kafka: Sent weather report for station {station['id']}")
    except Exception as e:
        print(f"Failed to send weather report for {station['id']}: {e}")

    return weather_data

# my_location_url = f"https://api.weather.gov/gridpoints/{station['id']}/90,48/forecast/hourly"
# point_report = requests.get("https://api.weather.gov/points/41,-95.74")
# print(f"STATUS: {point_report.status_code}")
# pprint(point_report.json())

# forecast = requests.get(my_location_url)
# print(f"STATUS: {forecast.status_code}")
# pprint(forecast.json()['properties']['periods'][0])

if __name__ == "__main__":
    operator = DBOperator(table='sources')
    stations = operator.query([{'type': 'NOAA-NWS'}])
    print(f"Total stations found: {len(stations)}")
    operator.close()

    weather_reports = []
    for station in stations:
        report = nws_weather(station)
        if report:
            weather_reports.append(report)
        else:
            print(f"No weather report generated for station {station['id']}")

    failures = []
    met = DBOperator(table='meteorology')
    for entity in weather_reports:
        pprint(entity)
        try:
            print("Adding NWS weather report to met table")
            met.add(entity.copy())
            met.commit()
        except Exception as e:
            print(f"An error occurred saving weather report...\n{e}")
            failures.append(entity)
    met.close()

    if failures:
        with open('nws-weather-failures.csv', 'a', newline='') as outFile:
            writer = csv.DictWriter(outFile, delimiter=',', fieldnames=failures[0].keys())
            writer.writeheader()
            for goob in failures:
                writer.writerow(goob)
    producer.flush()
    producer.close()

























