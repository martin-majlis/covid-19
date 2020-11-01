PYTHON=python3.7
GIT=git

DIR_ROOT=./
DIR_DATA=$(DIR_ROOT)/data
DIR_DATA_SUPPORT=$(DIR_DATA)/support/
DIR_DATA_BACKUP=$(DIR_DATA)/backup/
DIR_DATA_DERIVED=$(DIR_DATA)/derived/

F_NUTS_RAW=$(DIR_DATA_SUPPORT)/nuts-raw.csv
F_NUTS_ENRICHED=$(DIR_DATA_SUPPORT)/nuts-enriched.csv

DIR_MZCR_V1=$(DIR_DATA_BACKUP)/onemocneni-aktualne.mzcr.cz_covid-19/
API_MZCR_V1=https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/
DIR_MZCR_V2=$(DIR_DATA_BACKUP)/onemocneni-aktualne.mzcr.cz_covid-19-v2/
API_MZCR_V2=https://onemocneni-aktualne.mzcr.cz/api/v2/covid-19/

DIR_CSSEGI=$(DIR_DATA_BACKUP)/CSSEGISandData_COVID-19/csse_covid_19_time_series/
API_CSSEGI=https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/

DIR_DERIVED_MZCR=$(DIR_DATA_DERIVED)/onemocneni-aktualne.mzcr.cz_covid-19/

install: install-python-requirements

download=$(PYTHON) -c "from scripts.utils import download; download('$1', '$2', 0); import time; time.sleep(5);"

install-python-requirements:
	$(PYTHON) -m pip install -r scripts/requirements.txt


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)


download: download-onemocneni-aktualne.mzcr.cz_covid-19 download-CSSEGI

download-onemocneni-aktualne.mzcr.cz_covid-19: download-onemocneni-aktualne.mzcr.cz_covid-19-v1 download-onemocneni-aktualne.mzcr.cz_covid-19-v2

download-onemocneni-aktualne.mzcr.cz_covid-19-v1:
	mkdir -p ${DIR_MZCR_V1}
	$(call download,$(API_MZCR_V1)testy.csv,$(DIR_MZCR_V1)test.csv)
	$(call download,$(API_MZCR_V1)testy.json,$(DIR_MZCR_V1)test.json)
	$(call download,$(API_MZCR_V1)nakaza.csv,$(DIR_MZCR_V1)nakaza.csv)
	$(call download,$(API_MZCR_V1)nakaza.json,$(DIR_MZCR_V1)nakaza.json)
	$(call download,$(API_MZCR_V1)osoby.csv,$(DIR_MZCR_V1)osoby.csv)
	$(call download,$(API_MZCR_V1)osoby.json,$(DIR_MZCR_V1)osoby.json)
	$(call download,$(API_MZCR_V1)pomucky.csv,$(DIR_MZCR_V1)pomucky.csv)
	$(call download,$(API_MZCR_V1)pomucky.json,$(DIR_MZCR_V1)pomucky.json)
	$(call download,$(API_MZCR_V1)nakazeni-vyleceni-umrti-testy.csv,$(DIR_MZCR_V1)nakazeni-vyleceni-umrti-testy.csv)
	$(call download,$(API_MZCR_V1)nakazeni-vyleceni-umrti-testy.json,$(DIR_MZCR_V1)nakazeni-vyleceni-umrti-testy.json)
	$(call download,https://onemocneni-aktualne.mzcr.cz/covid-19,$(DIR_MZCR_V1)covid-19.html)

download-onemocneni-aktualne.mzcr.cz_covid-19-v2:
	mkdir -p ${DIR_MZCR_V2}
	$(call download,$(API_MZCR_V2)testy.csv,$(DIR_MZCR_V2)testy.csv)
	$(call download,$(API_MZCR_V2)testy.json,$(DIR_MZCR_V2)testy.json)
	$(call download,$(API_MZCR_V2)nakaza.csv,$(DIR_MZCR_V2)nakaza.csv)
	$(call download,$(API_MZCR_V2)nakaza.json,$(DIR_MZCR_V2)nakaza.json)
	$(call download,$(API_MZCR_V2)nakazeni-vyleceni-umrti-testy.csv,$(DIR_MZCR_V2)nakazeni-vyleceni-umrti-testy.csv)
	$(call download,$(API_MZCR_V2)nakazeni-vyleceni-umrti-testy.json,$(DIR_MZCR_V2)nakazeni-vyleceni-umrti-testy.json)
	$(call download,$(API_MZCR_V2)vyleceni.csv,$(DIR_MZCR_V2)vyleceni.csv)
	$(call download,$(API_MZCR_V2)vyleceni.json,$(DIR_MZCR_V2)vyleceni.json)
	$(call download,$(API_MZCR_V2)umrti.csv,$(DIR_MZCR_V2)umrti.csv)
	$(call download,$(API_MZCR_V2)umrti.json,$(DIR_MZCR_V2)umrti.json)
	$(call download,$(API_MZCR_V2)osoby.csv,$(DIR_MZCR_V2)osoby.csv)
	$(call download,$(API_MZCR_V2)osoby.json,$(DIR_MZCR_V2)osoby.json)
	$(call download,$(API_MZCR_V2)kraj-okres-nakazeni-vyleceni-umrti.csv,$(DIR_MZCR_V2)kraj-okres-nakazeni-vyleceni-umrti.csv)
	$(call download,$(API_MZCR_V2)kraj-okres-nakazeni-vyleceni-umrti.json,$(DIR_MZCR_V2)kraj-okres-nakazeni-vyleceni-umrti.json)
	$(call download,$(API_MZCR_V2)pomucky.csv,$(DIR_MZCR_V2)pomucky.csv)
	$(call download,$(API_MZCR_V2)pomucky.json,$(DIR_MZCR_V2)pomucky.json)

sort: sort-onemocneni-aktualne.mzcr.cz_covid-19-v1 sort-onemocneni-aktualne.mzcr.cz_covid-19-v2

sort-onemocneni-aktualne.mzcr.cz_covid-19-v1:
	head -n1 $(DIR_MZCR_V1)osoby.csv > $(DIR_MZCR_V1)osoby-sorted.csv
	tail -n +2 $(DIR_MZCR_V1)osoby.csv | sort >> $(DIR_MZCR_V1)osoby-sorted.csv

sort-onemocneni-aktualne.mzcr.cz_covid-19-v2:
	head -n1 $(DIR_MZCR_V2)osoby.csv > $(DIR_MZCR_V2)osoby-sorted.csv
	tail -n +2 $(DIR_MZCR_V2)osoby.csv | sort >> $(DIR_MZCR_V2)osoby-sorted.csv

download-CSSEGI:
	$(call download,$(API_CSSEGI)time_series_covid19_confirmed_global.csv,$(DIR_CSSEGI)time_series_covid19_confirmed_global.csv)
	$(call download,$(API_CSSEGI)time_series_covid19_deaths_global.csv,$(DIR_CSSEGI)time_series_covid19_deaths_global.csv)
	$(call download,$(API_CSSEGI)time_series_covid19_recovered_global.csv,$(DIR_CSSEGI)time_series_covid19_recovered_global.csv)

transform-CSSEGISandData-COVID:
	$(PYTHON) ./scripts/transform-CSSEGISandData-COVID-19.py

transform-oa-mzcr-covid: transform-oa-mzcr-covid-web transform-oa-mzcr-covid-pomucky

transform-oa-mzcr-covid-pomucky:
	$(PYTHON) ./scripts/transform_oa_mzcr_covid.py $(DIR_ROOT) $(DIR_MZCR_V1) $(DIR_DERIVED_MZCR)

transform-oa-mzcr-covid-web:
	cat $(DIR_MZCR_V1)covid-19.html | \
	tr '\n' ' ' | \
	sed -r 's/^\s+//g;s/(\[|\]|\}|\{)/\n\1\n/g;s/>/>\n/g;s/</\n</g;s/^\s+//g' > $(DIR_DERIVED_MZCR)covid-19.html

transform: transform-CSSEGISandData-COVID transform-oa-mzcr-covid

update-data:
	echo "BEGIN UPDATE - "`date` && \
	$(GIT) pull && \
	$(MAKE) download && \
	$(GIT) commit -a -q -m "Automatic data update - download - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	$(MAKE) sort && \
	$(GIT) commit -a -q -m "Automatic data update - sort - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	$(MAKE) transform && \
	$(GIT) commit -a -q -m "Automatic data update - transform - $(shell date --rfc-3339=seconds -u)" && \
	$(GIT) push && \
	echo "END UPDATE - "`date`
