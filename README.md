# covid-19-data


# Postup

1. Ziskat NUTS data
    1. [Klasifikace CZ-NUTS](https://www.czso.cz/csu/czso/klasifikace-uzemnich-statistickych-jednotek-cz-nuts)
    2. Prekonvertovat PDF na [CSV](support/nuts-raw.csv)
    3. Pridat souradnice [CSV](support/nuts-enriched.csv) pomoci `make nuts-enrichment`