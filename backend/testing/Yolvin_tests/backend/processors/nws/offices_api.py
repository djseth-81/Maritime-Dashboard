import os
import csv
import sys
import requests
from pprint import pprint
from ...DBOperator import DBOperator

"""
IGNORE ME! Just getting details for stations, not used for consistent API calls!
"""
# Retrieve OpenWeather API Token
# https://openweathermap.org/api/geocoding-api#direct
TOKEN = os.environ.get("TOKEN")
if TOKEN is None:
    sys.exit("No API Token provided.")

wfos = "afc,afg,ajk,bou,gjt,pub,lot,ilx,ind,iwx,dvn,dmx,ddc,gld,top,ict,jkl,lmk,pah,dtx,apx,grr,mqt,dlh,mpx,eax,sgf,lsx,gid,lbf,oax,bis,fgf,abr,unr,fsd,grb,arx,mkx,cys,riw,car,gyx,box,phi,aly,bgm,buf,okx,mhx,rah,ilm,cle,iln,pbz,ctp,chs,cae,gsp,btv,lwx,rnk,akq,rlx,gum,hfo,bmx,hun,mob,lzk,jax,key,mlb,mfl,tae,tbw,ffc,lch,lix,shv,jan,abq,oun,tsa,sju,meg,mrx,ohx,ama,ewx,bro,crp,epz,fwd,hgx,lub,maf,sjt,fgz,psr,twc,eka,lox,sto,sgx,mtr,hnx,boi,pih,byz,ggw,tfx,mso,lkn,vef,rev,mfr,pdt,pqr,slc,sew,otx".upper().split(',')

stations = []
failures = []

for wfo in wfos:
    station_url = f"https://api.weather.gov/offices/{wfo}"
    station = requests.get(station_url)
    if station.status_code not in [200, 201]:
        print(f"Error trying to retrieve timezone for {wfo}:\n{station.text}")
        # failures.append(wfo)
        continue
    # pprint(station.json())

    # TODO: Format and port into DB
    address = station.json()['address']
    tele = station.json()['telephone']
    # observation_stations = station.json()['approvedObservationStations']
    station_id = station.json()['id']
    station_name = station.json()['name']
    # forecast_zones = [i.split('/')[-1] for i in station.json()['responsibleForecastZones']]
    # responsible_zones = station.json()['responsibleCounties']

    # Using OpenWeather API to geocode address provided by WFO station
    guh = requests.get(f"http://api.openweathermap.org/geo/1.0/zip?zip={address['postalCode'].split('-')[0]},US&appid={TOKEN}")
    if guh.status_code not in [200, 201]:
        print(f"Error trying to retrieve timezone for {wfo}:\n{guh.text}")
        # failures.append(wfo)
        continue
    # pprint(guh.json())

    waaah = requests.get(f"https://api.weather.gov/points/{guh.json()['lat']},{guh.json()['lon']}")
    print(f'STATUS: {waaah.status_code}')
    if waaah.status_code not in [200, 201]:
        print(f"Error trying to retrieve timezone for {wfo}:\n{waaah.text}")
        # failures.append(wfo)
        continue
    # pprint(waaah.json()['properties']['timeZone'])

    stations.append({
            'id': station_id,
            'name': station_name,
            'region': f"USA-{address['addressRegion']}",
            'timezone': waaah.json()['properties']['timeZone'],
            'type': "NOAA-NWS",
            'geom': f"Point({guh.json()['lon']} {guh.json()['lat']})",
            'datums': ['Events', 'Meteorology']
        })

    # Do I save ???
    # print("Responsible forecast zones:") # datums ???
    # pprint(forecast_zones)

    # Do I save the following?
    # print("Address:")
    # pprint(address)
    # print(f"Phone: {tele}")
    # fire_zones = station.json()['responsibleFireZones']
    # print("Responsible Fire zones:")
    # pprint(fire_zones)
    # print("Approved subsidiary stations:")
    # pprint(observation_stations)
    # input("### API Script: Continue?")

print(f"{len(stations)}/{len(wfos)} stations are set to be added")
input()

operator = DBOperator(table='sources')

for entity in stations:
    try:
        print("Adding NWS station to sources table")
        operator.add(entity.copy())
        operator.commit()
    except Exception as e:
        print(f"An error occured adding station to DB...\n{e}")
        print("This station caused the failure:")
        pprint(entity)
        input() # DEBUG
        failures.append(entity)
operator.close()

if len(failures) > 0:
    with open('nws-stations-failures.csv', 'w', newline='') as outFile:
        writer = csv.DictWriter(outFile, delimiter=',',
                                fieldnames=failures[0].keys())
        writer.writeheader()
        for goob in failures:
            writer.writerow(goob)






















