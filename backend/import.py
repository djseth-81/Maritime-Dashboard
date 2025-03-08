import os
import csv
import sys
import requests
from pprint import pprint
from json import loads, dumps

"""
// TODO
- Get Headers for CSVs I have downloaded!
    - Figure out how to map them to my tables!
- Finish writing database.sql!
- See what kind of fields I'm working with using APIs!
    - GFW
"""

# sources
gfw_vessel_url = "https://gateway.api.globalfishingwatch.org/v3/vessels/search?query=mmsi&datasets[0]=public-global-vessel-identity:latest&includes[0]=MATCH_CRITERIA&includes[1]=OWNERSHIP&includes[2]=AUTHORIZATIONS&limit=1"

gfw_events_url = "https://gateway.api.globalfishingwatch.org/v3/events?datasets[0]=public-global-fishing-events:latest&start-date=2023-01-01&end-date=2024-01-31&limit=1&offset=0"

# GFW_TOKEN = os.environ.get("TOKEN")

# if GFW_TOKEN == None:
#     sys.exit("No GFW API Token provided.")
#
# gfw_headers = {
#     "Authorization": f"Bearer {GFW_TOKEN}"
# }


"""
GFW Data
"""
# gfw_vessel = requests.request("GET",gfw_vessel_url, headers=gfw_headers)
# print(gfw_vessel.status_code)

# gfw_events = requests.get(gfw_events_url, headers=gfw_headers)
# print(gfw_events.status_code)

# if __name__ == "__main__":
#     print("I'm HERE TO IMPORT CSV and API data!")
