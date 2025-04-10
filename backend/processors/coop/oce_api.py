import requests
from ...DBOperator import DBOperator

sources = DBOperator(table='sources')
oce = DBOperator(table='oceanography')

stations = sources.query([{'type':'NOAA-COOP'}])

datums = "water_temperature conductivity salinity water_level hourly_height high_low daily_mean monthly_mean one_minute_water_level predictions air_gap currents currents_predictions ofs_water_level".split()

url = f"https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?date=latest&station={station['id']}&product={product}&datum=STND&time_zone=gmt&units=english&format=json"
