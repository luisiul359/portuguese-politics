SHELL=/bin/bash

.PHONY = setup init test clean

# Defines the default target that `make` will try to make, or in the case of a phony target, execute the specified commands
# This target is executed whenever we just type `make`
.DEFAULT_GOAL = test

# This will install the package manager Poetry
setup:
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | ${PYTHON} -
	@echo "Done."

init:
	poetry install

deploy:
	poetry export -f requirements.txt --output requirements.txt
	func azure functionapp publish PortuguesePoliticsDailyUpdate

test:
	#mkdir -p data
	poetry run pytest **/tests # --cov=. --cov-report=xml:data/unit_coverage.xml

clean:
	rm -r .venv 