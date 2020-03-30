#!/usr/bin/env python3

# Adds extra columns into

import csv
import sys
import time

from geopy.geocoders import Nominatim

COLUMN_NUTS3 = 4
COLUMN_NUTS4 = 5

geolocator = Nominatim(
    user_agent="https://github.com/martin-majlis/covid-19-data"
)

reader = csv.reader(sys.stdin.readlines())
writer = csv.writer(sys.stdout)

# copy header and add two more columns
header = next(reader)
writer.writerow(header + ['Latitude', 'Longitude'])
for line in reader:
    extra = ['', '']
    for col in [COLUMN_NUTS3, COLUMN_NUTS4]:
        if line[col]:
            location = geolocator.geocode(line[COLUMN_NUTS3])
            if location:
                extra = [location.latitude, location.longitude]
            print(line[col] + " location: " + str(extra), file=sys.stderr)
            time.sleep(1)

    writer.writerow(line + extra)
