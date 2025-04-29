import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from ...DBOperator import DBOperator

"""
// IGNORE ME! Don't think this is necessary

// Uh oh
- Noticed that a vessel's MMSI can change
    - Their IMO does not, tho
    - GFW states it's because the vessel can change AIS transmission, or
        - inconsistently transmit the same ID values
        - change owners, callsign, or transmitters
"""
def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    # pprint(response.json())
    return response.json()

GFW_TOKEN = os.environ.get("TOKEN")

if GFW_TOKEN == None:
    sys.exit("No GFW API Token provided.")

operator = DBOperator(table='vessels')

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

vessels = operator.query([ # These don't have ANY details from the API
    {'src':'GFW-gfw'},
    {'src':'GFW-AIS'},
    {'src':'GFW-false_positives'},
    {'src':'GFW-crowd_sourced'},
    {'src':'GFW-dalhousie_longliner'},
])

pprint(vessels)
input()

for vessel in vessels:
    mmsi = vessel['mmsi']

    vessel_url = f"https://gateway.api.globalfishingwatch.org/v3/vessels/search?query={mmsi}&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"

    result = query(vessel_url)
    pprint(result)

    input()

operator.close()
