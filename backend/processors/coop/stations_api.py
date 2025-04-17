import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from ...DBOperator import DBOperator

sources = DBOperator(db="capstone",table="sources")
coop_stations_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
failures = []
dubs = 0

r = requests.get(coop_stations_url)
print(f"STATUS: {r.status_code}")
data = r.json()

# pprint(data.keys())
# Metadata
count = data['count']
units = data['units']

# for station in data['stations']:
#     pprint(station['name'])

station = data['stations']
for station in data['stations']:
    # build apis array because I'm way too lazy
    products = []
    for product in "air_temperature wind water_temperature air_pressure humidity conductivity visibility salinity water_level hourly_height high_low daily_mean monthly_mean one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level".split():
        url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={station['id']}&product={product}&datum=STND&time_zone=gmt&units=english&format=json"
        res = requests.get(url)
        # if we get valid data from product query (and it's not an error message), record it as valid station datum
        if (res.status_code == 200) and ('error' not in res.json().keys()):
            products.append(product)

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

    # Build station entity
    entity = {
        "id": station['id'],
        "name": station['name'],
        "region": "USA",
        "type": f"NOAA-COOP", # Cannot be "API"
        "datums": products, # Check if URI returns 200 or not
        # Following CANNOT BE NULL
        "timezone": f"{station['timezone']} (GMT {station['timezonecorr']})",
        "geom": f"Point({station['lng']} {station['lat']})",
    }

    try:
        print(f"Adding entity to db...")
        sources.add(entity.copy())
        sources.commit()
        dubs += 1
    except Exception as e:
        print(f"An error occured adding vessel to DB...\n{e}")
        print("This entity caused the failure:")
        pprint(entity)
        input()

        failures.append(entity)

print(f"{dubs} total pushes to DB.")
print(f"{len(failures)} total sources weren't added to DB for some reason.")

if len(failures) > 0:
    # TODO: DUNNO IF THE FOLLOWING ACCURATELY SAVES DATA
    with open('coop-failures.csv','w',newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',', fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)

sources.close()
