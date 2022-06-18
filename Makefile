SHELL=/bin/bash

.PHONY = setup init run run_extract test clean

# Defines the default target that `make` will try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = run

# This will install the package manager Poetry
setup:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | ${PYTHON} -
	@echo "Done."

init:
	poetry install

run:
	poetry run uvicorn src.app.main:app --reload

run_extract:
	time poetry run python src/parliament/extract.py

test:
	#mkdir -p data
	poetry run pytest tests # --cov=. --cov-report=xml:data/unit_coverage.xml

clean:
	rm -r .venv 