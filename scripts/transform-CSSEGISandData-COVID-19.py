#!/usr/bin/env python3

# This scripts converts data from https://onemocneni-aktualne.mzcr.cz/covid-19 to the format
# used by https://github.com/CSSEGISandData/COVID-19

import csv
import os
import time
from collections import defaultdict
from datetime import timedelta
from typing import Callable
from typing import Dict
from datetime import date
from typing import IO
from typing import List
from typing import Optional
from typing import Tuple
from hashlib import md5
import requests


def download(url: str, path: Optional[str] = None, cache_lifetime=3600) -> IO:
    if not path:
        path = '/tmp/' + md5(url.encode()).hexdigest()
    if not os.path.exists(path) or os.path.getmtime(path) < time.time() - cache_lifetime:
        response = requests.get(url, allow_redirects=True)
        print(f"Downloading {url} into {path}")
        with open(path, 'w') as fh:
            fh.write(response.text)
    print(f"{url} => {path}")
    return open(path, 'r')


def dt_format(d: date) -> str:
    # they are not using 0 padding - d.strftime("%m/%d/%y") :/
    return f"{d.month}/{d.day}/{d.year % 100}"


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


Counts = Dict[str, Dict[date, int]]


def load_czech_data(url: str) -> Tuple[Counts, Counts, Counts, Counts]:
    # aggregate statistics
    by_nuts3 = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
    by_age = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
    by_sex = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]
    by_sex_age = defaultdict(lambda: defaultdict(int))  # type: Dict[str, Dict[date, int]]

    czech_reader = csv.reader(download(url))
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

    return (
        by_nuts3,
        by_age,
        by_sex,
        by_sex_age,
    )


# load confirmed cases
confirmed_by_nuts3, confirmed_by_age, confirmed_by_sex, confirmed_by_sex_age = load_czech_data(
    url='https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.csv'
)

# load deaths
deaths_by_nuts3, deaths_by_age, deaths_by_sex, deaths_by_sex_age = load_czech_data(
    url='https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/umrti.csv'
)


# PROCESS NUTS DATA
# https://onemocneni-aktualne.mzcr.cz/covid-19

nuts_data = download(
    url='https://raw.githubusercontent.com/martin-majlis/covid-19-data/master/data/support/nuts-enriched.csv',
    path='/tmp/martin-majlis__covid-19-data__nuts-enriched.csv',
)

COLUMN_CODE = 'Kod'
COLUMN_NUTS3 = 'NUTS 3'
COLUMN_LATITUDE = 'Latitude'
COLUMN_LONGITUDE = 'Longitude'

nuts_reader = csv.DictReader(nuts_data)
# skip header
next(nuts_reader)

# use defaultdict of defaultdict to make it more robust
nuts_mapping = defaultdict(lambda: defaultdict(str))  # type: Dict[str, Dict[str, str]]
nuts_mapping.update({
    rec[COLUMN_CODE]: rec
    for rec in nuts_reader
})
# 2020-09-02: They have introduced NUT3 - CZ999
nuts_mapping['CZ999'] = {
    COLUMN_CODE: 'CZ999',
    COLUMN_NUTS3: '???',
    COLUMN_LATITUDE: 0.0,
    COLUMN_LONGITUDE: 0.0,
}

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

HEADER = COMMON_HEADERS + [dt_format(d) for d in DATES]
HEADER_ISO = COMMON_HEADERS + [d.isoformat() for d in DATES]


def raw_path(name: str) -> str:
    return 'data/CSSEGISandData-COVID-19/time_series/time_series_covid19_' + name + '.csv'


def transform_raw(
        name: str,
        data: Dict[str, Dict[date, int]],
        header: Callable[[str], Dict[str, str]]
):
    path = raw_path(name)
    with open(path, 'w') as csse_fh:
        csse_writer = csv.DictWriter(csse_fh, fieldnames=HEADER)
        csse_writer.writeheader()
        with open(path.replace('.csv', '_iso.csv'), 'w') as iso_fh:
            iso_writer = csv.DictWriter(iso_fh, fieldnames=HEADER_ISO)
            iso_writer.writeheader()

            for primary in sorted(data.keys()):
                values = data[primary]
                aggr = defaultdict(int)
                s = 0
                for d in DATES:
                    s += values[d]
                    aggr[d] = s
                csse_writer.writerow({
                    **header(primary),
                    **{
                        dt_format(d): v for d, v in aggr.items()
                    }
                })
                iso_writer.writerow({
                    **header(primary),
                    **{
                        d.isoformat(): v for d, v in aggr.items()
                    }
                })
    print(f"Raw transformation: {name} => {path}")

# transform confimed cases

transform_raw(
    name='confirmed_by_nut3',
    data=confirmed_by_nuts3,
    header=lambda k: {
        'Province/State': nuts_mapping[k][COLUMN_NUTS3],
        'Country/Region': 'Czechia',
        'Lat': nuts_mapping[k][COLUMN_LATITUDE],
        'Long': nuts_mapping[k][COLUMN_LONGITUDE],
    },
)

transform_raw(
    name='confirmed_by_age',
    data=confirmed_by_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='confirmed_by_sex',
    data=confirmed_by_sex,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='confirmed_by_sex_age',
    data=confirmed_by_sex_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

# transform deaths

transform_raw(
    name='deaths_by_nut3',
    data=deaths_by_nuts3,
    header=lambda k: {
        'Province/State': nuts_mapping[k][COLUMN_NUTS3],
        'Country/Region': 'Czechia',
        'Lat': nuts_mapping[k][COLUMN_LATITUDE],
        'Long': nuts_mapping[k][COLUMN_LONGITUDE],
    },
)

transform_raw(
    name='deaths_by_age',
    data=deaths_by_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='deaths_by_sex',
    data=deaths_by_sex,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='deaths_by_sex_age',
    data=deaths_by_sex_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)


def load_cssegi_data(url: str) -> List[Dict[str, str]]:
    cssegi_reader = csv.DictReader(download(url))
    # skip header
    next(cssegi_reader)

    return [rec for rec in cssegi_reader]


confirmed_cssegi_records = load_cssegi_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
deaths_cssegi_records = load_cssegi_data('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')


def combine_covidtrends(
        name: str,
        data: Dict[str, Dict[date, int]],
        modifier: Callable[[Dict[str, str]], Dict[str, str]]
):
    with open(raw_path(name)) as fh_raw:
        raw_reader = csv.DictReader(fh_raw)

        raw_data = [rec for rec in raw_reader]  # type: List[Dict[str, str]]

        path = f'data/derived/covidtrends/time_series_covid19_{name}_'
        with open(path + 'just_czechia.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=HEADER, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for rec in raw_data:
                writer.writerow(modifier(rec))

        with open(path + 'combined.csv', 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=HEADER, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            for rec in raw_data:
                writer.writerow(modifier(rec))
            for rec in data:
                writer.writerow(rec)

# combine confimed cases

combine_covidtrends(
    name='confirmed_by_nut3',
    data=confirmed_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)


combine_covidtrends(
    name='confirmed_by_age',
    data=confirmed_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='confirmed_by_sex',
    data=confirmed_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='confirmed_by_sex_age',
    data=confirmed_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

# combine deaths

combine_covidtrends(
    name='deaths_by_nut3',
    data=deaths_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)


combine_covidtrends(
    name='deaths_by_age',
    data=deaths_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='deaths_by_sex',
    data=deaths_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='deaths_by_sex_age',
    data=deaths_cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)
