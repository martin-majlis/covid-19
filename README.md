# covid-19-data

# Postup

1. Ziskat NUTS data
    1. [Klasifikace CZ-NUTS](https://www.czso.cz/csu/czso/klasifikace-uzemnich-statistickych-jednotek-cz-nuts)
    2. Prekonvertovat PDF na [CSV](data/support/nuts-raw.csv)
    3. Pridat souradnice [CSV](data/support/nuts-enriched.csv) pomoci `make nuts-enrichment`
   
2. Pomoci [skriptu](scripts/transform-CSSEGISandData-COVID-19.py) transformuj data
    1. Data pro [CR](data/CSSEGISandData-COVID-19/time_series)
    2. Data pro [covidtrends](data/derived/covidtrends)
