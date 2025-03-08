import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps

coop_stations_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"

# Meteorology
air_temp_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8594900&product=air_temperature&datum=STND&time_zone=gmt&units=english&format=json"

wind_url= "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8594900&product=wind&datum=STND&time_zone=gmt&units=english&format=json"

# Oceanography
water_temp_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station=8594900&product=water_temperature&datum=STND&time_zone=gmt&units=english&format=json"

wdc_metadata_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/8594900.json?expand=details,sensors,floodlevels,datums,harcon,tidepredoffsets,products,disclaimers,notices&units=english"

# coop_stations = requests.get(coop_stations_url)
# print(f"STATUS: {coop_stations.status_code}")
# pprint(coop_stations.json()['stations'][0])

# wdc_metadata = requests.get(wdc_metadata_url)
# print(f"STATUS: {wdc_metadata.status_code}")
# pprint(wdc_metadata.json())

"""
NOTES
- Can't think of a way to determine what met/ocean data can be retrieved with datagetter
    - short of just trying each one, that is
        - Generate string of product data to collect off of STATUS
        - This might just have to be the move then lol
            - worried I might get flagged for it lol
- Extrapolate to entire NOAA MET zone station is located in?

// TODO
1. Get stations and their details
2. Iterate and build collectable datums from stations
3. Get historical datums from mdapi/*/{stationID}/datums.json
    - For further historical details
"""

air_temp = requests.get(air_temp_url)
print(f"STATUS: {air_temp.status_code}")
pprint(air_temp.json())

water_temp = requests.get(water_temp_url)
print(f"STATUS: {water_temp.status_code}")
pprint(water_temp.json())

wind = requests.get(wind_url)
print(f"STATUS: {wind.status_code}")
pprint(wind.json())

