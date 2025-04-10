import requests
from datetime import datetime
from pprint import pprint
from ...DBOperator import DBOperator

sources = DBOperator(table='sources')
met = DBOperator(table='meteorology')

stations = sources.query([{'type':'NOAA-COOP'}])

def request(id, product):
    res = requests.get(f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={id}&product={product}&datum=STND&time_zone=gmt&units=english&format=json")
    print(f"Status: {res.status_code}")
    return res.json()

def air_temp(station, thing = 'air_temperature'):
    if thing not in station['datums']:
        print(f"No {thing} to report")
        return
    data = request(station['id'],thing)
    # pprint(data)
    print(f"Air Temp: {data['data'][0]['v']}") # Farenheit?

def wind(station, thing = 'wind'):
    if thing not in station['datums']:
        print(f"No {thing} to report")
        return
    data = request(station['id'],thing)
    # pprint(data)
    print(f"Wind direction: {data['data'][0]['dr']} ({data['data'][0]['d']})") # deg?
    print(f"Wind speed: {data['data'][0]['s']}") # kts?

def visibility(station, thing = 'visibility'):
    if thing not in station['datums']:
        print(f"No {thing} to report")
        return
    data = request(station['id'],thing)
    # pprint(data)
    print(f"Visibility: {data['data'][0]['v']}") # nautical mi?

def humidity(station, thing = 'humidity'):
    if thing not in station['datums']:
        print(f"No {thing} to report")
        return
    data = request(station['id'],thing)
    # pprint(data)
    print(f"Humidity: {data['data'][0]['v']}") # bar?

for station in stations:
    print(f"# Station {station['name']}")
    print(f"timestamp: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}")
    air_temp(station)
    wind(station)
    visibility(station)
    humidity(station)
    print()
    # input()


datums_url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station[id]}/datums.json"

notices_url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station[id]}/notices.json"

















