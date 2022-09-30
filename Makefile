.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

BROWSER := open
define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '.eggs' -type d -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: dist
dist: clean ## builds source and wheel package
	python setup.py sdist bdist_wheel

.PHONY: release
release: dist ## package and upload a release
	twine upload dist/*

.PHONY: lint
lint: ## check style with pylint
	pylint gitformsaver tests

.PHONY: toy
toy:  ## run local toy server for manual tests
	python -m tests.run_local

.PHONY: install
install: ## install the package with dev dependencies
	pip install -e . -r requirements_dev.txt

.PHONY: sync
sync: ## completely sync installed packages with dev dependencies
	pip-sync requirements_dev.txt
	pip install -e .

.PHONY: lock
lock:
	pip-compile-multi --directory . --allow-unsafe --no-upgrade -t requirements_dev.in

.PHONY: upgrade
upgrade:
	pip-compile-multi --directory . --allow-unsafe -t requirements_dev.in
