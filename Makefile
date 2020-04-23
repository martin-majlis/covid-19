PYTHON=python3.7
GIT=git

DIR_ROOT=./
DIR_DATA=$(DIR_ROOT)/data
DIR_DATA_SUPPORT=$(DIR_DATA)/support/
DIR_DATA_BACKUP=$(DIR_DATA)/backup/
DIR_DATA_DERIVED=$(DIR_DATA)/derived/

F_NUTS_RAW=$(DIR_DATA_SUPPORT)/nuts-raw.csv
F_NUTS_ENRICHED=$(DIR_DATA_SUPPORT)/nuts-enriched.csv

DIR_MZCR=$(DIR_DATA_BACKUP)/onemocneni-aktualne.mzcr.cz_covid-19/
API_MZCR=https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/

DIR_CSSEGI=$(DIR_DATA_BACKUP)/CSSEGISandData_COVID-19/csse_covid_19_time_series/
API_CSSEGI=https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/

DIR_DERIVED_MZCR=$(DIR_DATA_DERIVED)/onemocneni-aktualne.mzcr.cz_covid-19/

install: install-python-requirements

download=$(PYTHON) -c "from scripts.utils import download; download('$1', '$2', 0)"

install-python-requirements:
	$(PYTHON) -m pip install -r scripts/requirements.txt


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)


download: download-onemocneni-aktualne.mzcr.cz_covid-19 download-CSSEGI

download-onemocneni-aktualne.mzcr.cz_covid-19:
	$(call download,$(API_MZCR)testy.csv,$(DIR_MZCR)test.csv)
	$(call download,$(API_MZCR)testy.json,$(DIR_MZCR)test.json)
	$(call download,$(API_MZCR)nakaza.csv,$(DIR_MZCR)nakaza.csv)
	$(call download,$(API_MZCR)nakaza.json,$(DIR_MZCR)nakaza.json)
	$(call download,$(API_MZCR)osoby.csv,$(DIR_MZCR)osoby.csv)
	$(call download,$(API_MZCR)osoby.json,$(DIR_MZCR)osoby.json)
	$(call download,$(API_MZCR)pomucky.csv,$(DIR_MZCR)pomucky.csv)
	$(call download,$(API_MZCR)pomucky.json,$(DIR_MZCR)pomucky.json)
	$(call download,https://onemocneni-aktualne.mzcr.cz/covid-19,$(DIR_MZCR)covid-19.html)

sort: sort-onemocneni-aktualne.mzcr.cz_covid-19

sort-onemocneni-aktualne.mzcr.cz_covid-19:
	head -n1 $(DIR_MZCR)osoby.csv > $(DIR_MZCR)osoby-sorted.csv
	tail -n +2 $(DIR_MZCR)osoby.csv | sort >> $(DIR_MZCR)osoby-sorted.csv

download-CSSEGI:
	$(call download,$(API_CSSEGI)time_series_covid19_confirmed_global.csv,$(DIR_CSSEGI)time_series_covid19_confirmed_global.csv)
	$(call download,$(API_CSSEGI)time_series_covid19_deaths_global.csv,$(DIR_CSSEGI)time_series_covid19_deaths_global.csv)
	$(call download,$(API_CSSEGI)time_series_covid19_recovered_global.csv,$(DIR_CSSEGI)time_series_covid19_recovered_global.csv)

transform-CSSEGISandData-COVID:
	$(PYTHON) ./scripts/transform-CSSEGISandData-COVID-19.py

transform-oa-mzcr-covid:
	$(PYTHON) ./scripts/transform_oa_mzcr_covid.py $(DIR_ROOT) $(DIR_MZCR) $(DIR_DERIVED_MZCR)
	cat $(DIR_MZCR)covid-19.html | \
	tr '\n' ' ' | \
	sed -r 's/^\s+//g;s/(\[|\]|\}|\{)/\n\1\n/g;s/>/>\n/g;s/</\n</g;s/^\s+//g' > $(DIR_DERIVED_MZCR)covid-19.html

transform: transform-CSSEGISandData-COVID transform-oa-mzcr-covid

update-data:
	echo "BEGIN UPDATE - "`date` && \
	$(GIT) pull && \
	$(MAKE) download && \
	$(GIT) commit -a -m "Automatic data update - download - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	$(MAKE) sort && \
	$(GIT) commit -a -m "Automatic data update - sort - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	$(MAKE) transform && \
	$(GIT) commit -a -m "Automatic data update - transform - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	echo "END UPDATE - "`date`
