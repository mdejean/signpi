#!/usr/bin/python3

import requests
import json
import pickle
import sys
from config import *

headers = {'x-application': 'signpi', 'x-api-key': api_key}
try:
    with requests.get(goodservice_url) as req:
        body = req.json()

        #    now = body['timestamp']

        # TODO: both directions, filter routes
        trips = body['upcoming_trips'][direction]

        #    for n in range(min(4, len(trips))):
        #        t = trips[n]
        #        eta_min = round((t['estimated_current_stop_arrival_time'] - now) / 60)

        #        print(f"{n}. {t['route_id']} {t['destination_stop']} {eta_min} min")

        with open('trips.json', 'w') as f:
            json.dump(trips[:min(4, len(trips))], f)
except ConnectionError:
    with open('trips.json') as f:
        json.dump([], f)
    sys.exit(1)
