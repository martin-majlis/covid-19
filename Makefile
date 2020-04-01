PYTHON=python3.7
GIT=git

DIR_DATA=data
DIR_DATA_SUPPORT=$(DIR_DATA)/support/
DIR_DATA_BACKUP=$(DIR_DATA)/backup/

F_NUTS_RAW=$(DIR_DATA_SUPPORT)/nuts-raw.csv
F_NUTS_ENRICHED=$(DIR_DATA_SUPPORT)/nuts-enriched.csv

DIR_MZCR=$(DIR_DATA_BACKUP)/onemocneni-aktualne.mzcr.cz_covid-19/
API_MZCR=https://onemocneni-aktualne.mzcr.cz/api/v1/covid-19/

install: install-python-requirements

download=$(PYTHON) -c "from scripts.utils import download; download('$1', '$2')"

install-python-requirements:
	$(PYTHON) -m pip install -r scripts/requirements.txt


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)


download: download-onemocneni-aktualne.mzcr.cz_covid-19

download-onemocneni-aktualne.mzcr.cz_covid-19:
	$(call download,$(API_MZCR)testy.csv,$(DIR_MZCR)test.csv)
	$(call download,$(API_MZCR)testy.json,$(DIR_MZCR)test.json)
	$(call download,$(API_MZCR)nakaza.csv,$(DIR_MZCR)nakaza.csv)
	$(call download,$(API_MZCR)nakaza.json,$(DIR_MZCR)nakaza.json)
	$(call download,$(API_MZCR)osoby.csv,$(DIR_MZCR)osoby.csv)
	$(call download,$(API_MZCR)osoby.json,$(DIR_MZCR)osoby.json)
	$(call download,$(API_MZCR)pomucky.csv,$(DIR_MZCR)pomucky.csv)
	$(call download,$(API_MZCR)pomucky.json,$(DIR_MZCR)pomucky.json)

http://google.cz => /tmp/google.cz
transform-CSSEGISandData-COVID:
	$(PYTHON) ./scripts/transform-CSSEGISandData-COVID-19.py

transform: transform-CSSEGISandData-COVID

update-data:
	$(GIT) pull && \
	$(MAKE) download transform && \
	$(GIT) commit -a -m "Automatic data update - $(shell date --rfc-3339=seconds -u)"
