#!/usr/bin/env python3
import csv
import os
import time
from collections import defaultdict
from datetime import timedelta
from typing import Callable
from typing import Dict
from typing import IO
from datetime import date
from typing import List

import requests

CACHE_LIFETIME = 3 * 3600


def download(url: str, name: str) -> IO:
    path = '/tmp/' + name
    if not os.path.exists(path) or os.path.getmtime(path) < time.time() - CACHE_LIFETIME:
        response = requests.get(url, allow_redirects=True)
        with open(path, 'w') as fh:
            fh.write(response.text)

    return open(path, 'r')

# PROCESS NUTS DATA
# https://onemocneni-aktualne.mzcr.cz/covid-19

nuts_data = download(
    url='https://raw.githubusercontent.com/martin-majlis/covid-19-data/master/support/nuts-enriched.csv',
    name='nuts-enriched.csv',
)

COLUMN_CODE = 0
COLUMN_LATITUDE = 5
COLUMN_LONGITUDE = 6

# PROCESS CZECH DATA
# https://onemocneni-aktualne.mzcr.cz/covid-19


age_buckets = {
    14:    '0–14',
    24:    '15–24',
    34:    '25–34',
    44:    '35–44',
    54:    '45–54',
    64:    '55–64',
    1_000: '65+',
}


def age2bucket(age: int) -> str:
    for limit, label in age_buckets.items():
        if age <= limit:
            return label


COLUMN_DATE = 0
COLUMN_AGE = 1
COLUMN_SEX = 2
COLUMN_REGION = 3


# get data for Czech Republic
czech_data = download(
    url='https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.csv',
    name='osoby.csv',
)

# aggregate statistics
by_nuts3 = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
by_age = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
by_sex = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
by_sex_age = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]

czech_reader = csv.reader(czech_data)
# skip header
next(czech_reader)
for line in czech_reader:
    d = date.fromisoformat(line[COLUMN_DATE])
    age = int(line[COLUMN_AGE])
    sex = line[COLUMN_SEX]
    nuts3 = line[COLUMN_REGION]

    bucket = age2bucket(age)

    # stats
    by_nuts3[nuts3][d] += 1
    by_age[bucket][d] += 1
    by_sex[sex][d] += 1
    by_sex_age[sex + ": " + bucket][d] += 1


# PROCESS NUTS DATA
# https://onemocneni-aktualne.mzcr.cz/covid-19

nuts_data = download(
    url='https://raw.githubusercontent.com/martin-majlis/covid-19-data/master/support/nuts-enriched.csv',
    name='nuts-enriched.csv',
)

COLUMN_CODE = 'Kod'
COLUMN_NUTS3 = 'NUTS 3'
COLUMN_LATITUDE = 'Latitude'
COLUMN_LONGITUDE = 'Longitude'

nuts_reader = csv.DictReader(nuts_data)
# skip header
next(nuts_reader)

nuts_mapping = defaultdict(dict)  # type: Dict[str, Dict[str, str]]
nuts_mapping.update({
    rec[COLUMN_CODE]: rec
    for rec in nuts_reader
})

# GENERATE FINAL REPORTS

COMMON_HEADERS = [
    'Province/State',
    'Country/Region',
    'Lat',
    'Long',
]

# generate list of dates for final export
# https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv
DATES = []  # type: List[date]
d = date(2020, 1, 22)

while d < date.today():
    DATES.append(d)
    d += timedelta(days=1)


def generate(
        name: str,
        data: Dict[str, Dict[date, int]],
        header: Callable[[str], Dict[str, str]]
):
    path = 'time_series/time_series_' + name + '.csv'
    with open(path, 'w') as csvfile:
        fieldnames = COMMON_HEADERS + [d.strftime("%m/%d/%y") for d in DATES]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for primary in sorted(data.keys()):
            values = data[primary]
            aggr = defaultdict(int)
            s = 0
            for d in DATES:
                s += values[d]
                aggr[d.strftime("%m/%d/%y")] = s
            writer.writerow({
                **header(primary),
                **aggr
            })


generate(
    name='by_region',
    data=by_nuts3,
    header=lambda k: {
        'Province/State': nuts_mapping[k][COLUMN_NUTS3],
        'Country/Region': 'Czechia',
        'Lat': nuts_mapping[k][COLUMN_LATITUDE],
        'Long': nuts_mapping[k][COLUMN_LONGITUDE],
    },
)

generate(
    name='by_age',
    data=by_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

generate(
    name='by_sex',
    data=by_sex,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

generate(
    name='by_sex_age',
    data=by_sex_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)
