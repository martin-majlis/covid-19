PYTHON=python3.7

DIR_DATA=data
DIR_DATA_SUPPORT=$(DATA)/support/

F_NUTS_RAW=$(DIR_DATA_SUPPORT)/nuts-raw.csv
F_NUTS_ENRICHED=$(DIR_DATA_SUPPORT)/nuts-enriched.csv


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)

transform-CSSEGISandData-COVID:
	$(PYTHON) ./scripts/transform-transform-CSSEGISandData-COVID.py
