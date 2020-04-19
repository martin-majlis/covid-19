# MZCR.cz

It is using data from [mzcr.cz](../../backup/onemocneni-aktualne.mzcr.cz_covid-19) and transforms them with [transform_oa_mzcr_covid.py](../../../scripts/transform_oa_mzcr_covid.py) so that they can be further processed.

MZCR is publishing current data every day. But there is no way how to get historical data. To bypass this I am using [backups](../../backup/onemocneni-aktualne.mzcr.cz_covid-19) to reconstruct the time series.

## Data
  * [pomucky-simple.csv](pomucky-simple.csv) - list of tupples (kraj, pomucka, pocet, zmena)
  * [pomucky-dates.csv](pomucky-dates.csv) - value for given date is in the column
  * [pomucky-kraje.csv](pomucky-kraje.csv) - value for given region is in the column  