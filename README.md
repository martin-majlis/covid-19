# COVID-19

## Postup

1. Ziskej NUTS data
    1. [Klasifikace CZ-NUTS](https://www.czso.cz/csu/czso/klasifikace-uzemnich-statistickych-jednotek-cz-nuts)
    2. Prekonvertovat PDF na [CSV](data/support/nuts-raw.csv)
    3. Pridat souradnice [CSV](data/support/nuts-enriched.csv) pomoci `make nuts-enrichment`

2. Transformuj data
    1. Pouzij [skript](scripts/transform-CSSEGISandData-COVID-19.py)
    1. Data v [CSSEGIS](data/CSSEGISandData-COVID-19/time_series) formatu pro CR
    2. Data v [covidtrends](data/derived/covidtrends) formatu pro CR

3. Zobraz data:
    1. https://martin.majlis.cz/covidtrends/

## Data

* https://github.com/CSSEGISandData/COVID-19/
* https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19
