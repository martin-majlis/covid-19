#!/usr/bin/env python3

# This scripts converts data from https://onemocneni-aktualne.mzcr.cz/covid-19 to the format
# used by https://github.com/CSSEGISandData/COVID-19

import csv
from collections import defaultdict
from datetime import timedelta
from typing import Callable
from typing import Dict
from datetime import date
from typing import List

from scripts.utils import download


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


# get data for Czech Republic
czech_data = download(
    url='https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/osoby.csv',
    path='/tmp/osoby.csv',
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

HEADER = COMMON_HEADERS + [dt_format(d) for d in DATES]
HEADER_ISO = COMMON_HEADERS + [d.isoformat() for d in DATES]


def raw_path(name: str) -> str:
    return 'data/CSSEGISandData-COVID-19/time_series/time_series_covid19_confirmed_' + name + '.csv'


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


transform_raw(
    name='by_nut3',
    data=by_nuts3,
    header=lambda k: {
        'Province/State': nuts_mapping[k][COLUMN_NUTS3],
        'Country/Region': 'Czechia',
        'Lat': nuts_mapping[k][COLUMN_LATITUDE],
        'Long': nuts_mapping[k][COLUMN_LONGITUDE],
    },
)

transform_raw(
    name='by_age',
    data=by_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='by_sex',
    data=by_sex,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

transform_raw(
    name='by_sex_age',
    data=by_sex_age,
    header=lambda k: {
        'Province/State': k,
        'Country/Region': 'Czechia',
        'Lat': '',
        'Long': '',
    },
)

cssegi_data = download(
    url='https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv',
    path='/tmp/CSSEGISandData__COVID-19__time_series_covid19_confirmed_global.csv',
)

cssegi_reader = csv.DictReader(cssegi_data)
# skip header
next(cssegi_reader)

cssegi_records = [rec for rec in cssegi_reader]  # type: List[Dict[str, str]]


def combine_covidtrends(
        name: str,
        data: Dict[str, Dict[date, int]],
        modifier: Callable[[Dict[str, str]], Dict[str, str]]
):
    with open(raw_path(name)) as fh_raw:
        raw_reader = csv.DictReader(fh_raw)

        raw_data = [rec for rec in raw_reader]  # type: List[Dict[str, str]]

        path = f'data/derived/covidtrends/time_series_covid19_confirmed_{name}_'
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


combine_covidtrends(
    name='by_nut3',
    data=cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)


combine_covidtrends(
    name='by_age',
    data=cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='by_sex',
    data=cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)

combine_covidtrends(
    name='by_sex_age',
    data=cssegi_records,
    modifier=lambda rec: {
        **rec,
        **{
            'Province/State': ' ' + rec['Country/Region'],
            'Country/Region': ' ' + rec['Province/State'],
        },
    },
)
