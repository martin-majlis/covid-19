PYTHON=python3

F_NUTS_RAW=support/nuts-raw.csv
F_NUTS_ENRICHED=support/nuts-enriched.csv


nuts-enrichment:
	cat $(F_NUTS_RAW) | $(PYTHON) ./scripts/nuts_enrichment.py | tee $(F_NUTS_ENRICHED)
