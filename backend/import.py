import os
import sys
import csv
import requests
from pprint import pprint
from datetime import datetime
from json import loads, dumps
from DBOperator import DBOperator

"""
// TODO
- FIXME: DBOperator.add() hates entity['geom']

- RUN THIS SCRIPT
    - make sure the DBOperator.add() function works properly!
    - Make sure I can track failures to avoid duplicates and add them again later!
"""

vessels = DBOperator(db="capstone",table="vessels")

headers = "mmsi vessel_name callsign timestamp heading speed src type flag length width draft cargo_weight geom lat lon dist_from_shore dist_from_port".split()
with open("failures.csv", 'w',newline='') as outFile:
    writer = csv.writer(outFile, delimiter=',')
    writer.writerow(headers)

gfw_data = ['gfw-data/drifting_longlines.csv', 'gfw-data/fixed_gear.csv', 'gfw-data/pole_and_lines.csv', 'gfw-data/purse_seines.csv', 'gfw-data/trawlers.csv', 'gfw-data/trollers.csv']
others = 'gfw-data/unknown.csv'

for file in gfw_data:
    print(f"### Importing {file} to Vessels table...")
    with open(file, newline='') as inFile, open('failures.csv', 'a', newline='') as outFile:
        data = csv.reader(inFile, delimiter=',')
        headers = next(data, None)
        for row in data:
            entity = {}
            entity['mmsi'] = int(float(row[0])) # mmsi
            entity['vessel_name'] = ''
            entity['callsign'] = ''
            entity['timestamp'] = f"{datetime.fromtimestamp(int(float(row[1])))}".replace(" ","T") # timestamp
            entity['heading'] = round(float(row[5]), 2) # course (assuming degrees)
            entity['speed'] = round(float(row[4]), 2) # speed (assuming knots)
            if int(float(row[8])) > 0:
                entity['current_status'] = "fishing"
            else:
                entity['current_status'] = "anchored"
            entity['src'] =  f"GFW-{row[9]}" # source
            entity['type'] = "FISHING"
            entity['flag'] = "OTHER"
            entity['length'] = 0.0
            entity['width'] = 0.0
            entity['draft'] = 0.0
            entity['cargo_weight'] = 0.0
            entity['geom'] = None
            entity['lat'] = round(float(row[6]), 4) # lat
            entity['lon'] = round(float(row[7]), 4) # lon
            entity['dist_from_shore'] = round(float(row[2]), 2) / 1000 # dist_from_shore, assuming in m
            entity['dist_from_port'] = round(float(row[3]), 2) / 1000 # dist_from_port, assuming in m

            pprint(entity)
            print("Adding entity to db...")
            try:
                vessels.add(entity)
            except Exception:
                print("An error occured adding entity to failures CSV...")
                writer = csv.DictWriter(outFile, delimiter=',', fieldnames=entity.keys())
                writer.writerow(entity)
            input()
    vessels.commit()

with open(others, newline='') as inFile, open('failures.csv', 'a', newline='') as outFile:
    data = csv.reader(inFile, delimiter=',')
    headers = next(data, None)
    for row in data:
        entity = {}
        entity['mmsi'] = int(float(row[0])) # mmsi
        entity['vessel_name'] = ''
        entity['callsign'] = ''
        entity['timestamp'] = f"{datetime.fromtimestamp(int(float(row[1])))}".replace(" ","T") # timestamp
        entity['heading'] = round(float(row[5]), 2) # course (assuming degrees)
        entity['speed'] = round(float(row[4]), 2) # speed (assuming knots)
        entity['current_status'] = "unkown"
        entity['src'] =  f"GFW-{row[9]}" # source
        entity['type'] = "OTHER"
        entity['flag'] = "OTHER"
        entity['length'] = 0.0
        entity['width'] = 0.0
        entity['draft'] = 0.0
        entity['cargo_weight'] = 0.0
        entity['geom'] = None
        entity['lat'] = round(float(row[6]), 4) # lat
        entity['lon'] = round(float(row[7]), 4) # lon
        entity['dist_from_shore'] = round(float(row[2]), 2) / 1000 # dist_from_shore, assuming in m
        entity['dist_from_port'] = round(float(row[3]), 2) / 1000 # dist_from_port, assuming in m
            
        print("Adding entity to db...")
        try:
            vessels.add(entity)
        except:
            print("An error occured adding entity to failures CSV...")
            writer = csv.DictWriter(outFile, delimiter=',', fieldnames=headers)
            writer.writerow(entity)
        input()

cadastre='MarineCadastre_2024-12-30/AIS_2024_09_30.csv'

# Converting NAIS AIS ship identifier codes into our own vessel types
cargo = [i for i in range(70, 80)] + [1003, 1004, 1016]
fishing = [30, 1001, 1002]
tanker = [i for i in range(80, 90)] + [1017, 1024]
tug = [21, 22, 31, 32, 52, 1023, 1025]
passenger = [i for i in range(60,70)] + [1012, 1013, 1014, 1015]
recreational = [36, 37, 1019]

with open(cadastre, newline='') as inFile:
    data = csv.reader(inFile, delimiter=',')
    headers = next(data, None)
    for row in data:
        entity = {}
        entity['mmsi'] = int(float(row[0])) # mmsi
        entity['vessel_name'] = row[7]
        entity['callsign'] = row[9]
        entity['timestamp'] = row[1] # UTC datetime
        entity['course'] = round(float(row[5]), 2) # heading over ground degrees
        # entity['heading'] = row[6] # true heading degrees
        entity['speed'] = round(float(row[4]), 2) # knots
        entity['current_status'] = row[11]
        # print("voyage")
        entity['src'] = "MarineCadastre-AIS"
        # converging NAIS specs to TYPE
        ais_code = int(row[10])
        if ais_code in cargo:
            entity['type'] = "CARGO"
        elif ais_code in fishing:
            entity['type'] = "FISHING"
        elif ais_code in tanker:
            entity['type'] = "TANKER"
        elif ais_code in tug:
            entity['type'] = "TUG"
        elif ais_code in passenger:
            entity['type'] = "PASSENGER"
        elif ais_code in recreational:
            entity['type'] = "RECREATIONAL"
        else:
            entity['type'] = "OTHER"
        entity['flag'] = "USA"
        entity['length'] = round(float(row[12]), 2) # meters
        entity['width'] = round(float(row[13]), 2) # meters
        if len(row[14]) > 0:
            entity['draft'] = round(float(row[14]), 2) # meters
        else:
            entity['draft'] = 0.0
        if len(row[15]) > 0:
            entity['cargo_weight'] = round(float(row[15]), 2)
        else:
            entity['cargo_weight'] = 0.0
        entity['geom'] = None
        entity['lat'] = round(float(row[2]), 2)
        entity['lon'] = round(float(row[3]), 2)
        entity['dist_from_port'] = 0.0
        entity['dist_from_shore'] = 0.0
        # print(f"IMO: {row[8]}") # International Maritime Organization Vessel number
        # print(f"tranciever class: {row[16]}") # AIS tranciever class
        pprint(entity)
        print("Adding entity to DB...")
        try:
            vessels.add(entity)
        except:
            print("An error occured adding entity to failures CSV...")
            writer = csv.DictWriter(outFile, delimiter=',', fieldnames=headers)
            writer.writerow(entity)

