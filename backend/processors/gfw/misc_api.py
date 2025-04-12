import pytz
import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps
from datetime import datetime, timedelta
from DBOperator import DBOperator

def query(url: str) -> dict:
    response = requests.get(url, headers=headers)
    print(f"STATUS: {response.status_code}")
    # pprint(response.json())
    return response.json()

GFW_TOKEN = os.environ.get("TOKEN")

if GFW_TOKEN == None:
    sys.exit("No GFW API Token provided.")

headers = {
    "Authorization": f"Bearer {GFW_TOKEN}"
}

date = datetime.now()
utc = pytz.UTC

# Searching by id:
# id = '1da8dbc23-3c48-d5ce-95f1-1ffb6cc00161'
# vessel_url = f"https://gateway.api.globalfishingwatch.org/v3/vessels/search?query={id}&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS"
# entry = query(vessel_url)['entries'][0]
# pprint(entry)
# index = 0
# diff = date.year
# for i,item in enumerate(entry['combinedSourcesInfo']):
#     if (date.year - item['shiptypes'][0]['yearTo']) < diff: # If difference is smaller than previously recorded one, update
#         diff = date.year - item['shiptypes'][0]['yearTo']
#         print(f"Replacing index= {index} with more recent index= {i}")
#         index = i

# pprint(entry['combinedSourcesInfo'][index])

# # Parse selfReportedInfo for latest reported data
# # Looks like most recent entry is first element in array
# index = 0
# diff = timedelta(days=date.year)
# for i, item in enumerate(entry['selfReportedInfo']):
#     startDate = datetime.fromisoformat(item['transmissionDateFrom'])
#     endDate = datetime.fromisoformat(item['transmissionDateTo'])
#     # print(f"Transmission Start: {startDate}, Transmission End: {endDate}")
#     # print(f"Current Date: {date}")
#     # Event is in the past
#     # print(f"Event is in the past: {utc.localize(date) > endDate}")
#     # Event is currently in effect
#     # print(f"Event is currently in effect: {(utc.localize(date) >= startDate) and (utc.localize(date) <= endDate)}")
#     # Event has yet to happen
#     # print(f"Event has yet to happen: {(startDate > utc.localize(date))}")
#     # If event is currently in effect, or has past
#     # This solution sucks, but if the years match, pick this entry
#     if (utc.localize(date) - endDate <= diff):
#         print(f"Replacing old index= {index} with new index= {i}")
#         diff = endDate - utc.localize(date)
#         index = i

# pprint(entry['selfReportedInfo'][index])
# sys.exit()

# Fixed infrastructure: Dunno if this works (very likely won't cuz their API is tempermental
infra_url = "https://gateway.api.globalfishingwatch.org/v3/datasets/public-fixed-infrastructure-filtered:latest"
infra = query(infra_url)
pprint(infra)
# pprint(infra['entries'])
pprint(infra.keys())

# SAR and AIS Datasets <- I guess these are explicitly for GFW's map visualization API
data = { 
    "vessels": [
        {"datasetId": "public-global-fishing-effort:latest"}, # AIS Reporting
        {"datasetId": "public-global-sar-presence:latest"} # SAR Reporting
    ]
}
