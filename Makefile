PYTHON=python3.7
GIT=git

DIR_DATA=data
DIR_DATA_SUPPORT=$(DATA)/support/

F_NUTS_RAW=$(DIR_DATA_SUPPORT)/nuts-raw.csv
F_NUTS_ENRICHED=$(DIR_DATA_SUPPORT)/nuts-enriched.csv

install: install-python-requirements

install-python-requirements:
	$(PYTHON) -m pip install -r scripts/requirements.txt


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)

download:
	date

transform-CSSEGISandData-COVID:
	$(PYTHON) ./scripts/transform-CSSEGISandData-COVID-19.py

transform: transform-CSSEGISandData-COVID

update-data:
	$(GIT) pull && \
	$(MAKE) download transform && \
	$(GIT) commit -a -m "Update - $(shell date --rfc-3339=seconds -u)"
