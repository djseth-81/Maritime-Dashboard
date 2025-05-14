import os
import sys
import requests
from pprint import pprint
from json import dumps
from ..DBOperator import DBOperator
from datetime import datetime, timedelta
import pytz
from time import sleep
from kafka import KafkaProducer
import random
import string

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

# GFW Auth
OWM_TOKEN = os.environ.get("OWM_TOKEN")
if not OWM_TOKEN:
    sys.exit("No OpenWeatherMaps API Token provided.")

# Time setup
# utc = pytz.UTC

def osm_layer(layer: str) -> dict:
    now = datetime.now()
    url = f'https://tile.openweathermap.org/map/{layer}_new/0/0/0.png?appid=' + OWM_TOKEN
    print(url)

    response = requests.get(url)
    if response.status_code not in [200,201]:
        print(response.text)
        return None
    return {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "message": f"{layer} layer",
        'layer': response.text,
    }

def us_radar() -> dict:
    now = datetime.now()
    url = 'https://mesonet.agron.iastate.edu/cache/tile.py/1.0.0/ridge::BMX-N0Q-0/7/33/50.png'
    response = requests.get(url)
    if response.status_code not in [200,201]:
        print(response.text)
        return None
    return {
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "message": "US radar layer",
        'layer': response.text,
    }


if __name__ == "__main__":

    # while True:
    # for layer in "clouds precipitation wind temp".split():
    #     msg_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
    #     producer.send("Weather",key=msg_key,value=osm_layer(layer))
    #     print('Kafka: Sent OWM layer to Weather topic.')
    #     input()
    
    msg_key = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))
    producer.send("Weather",key=msg_key,value=us_radar())
    print('Kafka: Sent US radar layer to Weather topic. Now sleeping for 1 hr...')
    producer.flush()

        # sleep(3600) # sleep for 1 hr
