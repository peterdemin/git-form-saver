.DEFAULT_GOAL := help

BROWSER := open

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-10s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

.PHONY: help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

.PHONY: clean
clean: ## remove build artifacts
	rm -rf build/ \
	       docs/ \
	       _docs/ \
	       dist/ \
	       .eggs/
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
	pylint -j 0 gitformsaver tests
	mypy gitformsaver/
	pytype -j auto gitformsaver/

.PHONY: test
test: ## run test suite
	pytest --cov=gitformsaver tests

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
lock: ## lock versions of third-party dependencies
	pip-compile-multi --directory . --allow-unsafe --no-upgrade -t requirements_dev.in

.PHONY: upgrade
upgrade: ## upgrade versions of third-party dependencies
	pip-compile-multi --directory . --allow-unsafe -t requirements_dev.in

.PHONY: docs
docs: Makefile  ## build HTML docs
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)


# GitHub pages action:
.PHONY: gitconfig
gitconfig:  ## Configure git for commiting in GitHub actions workflow.
	git config user.name 'Peter Demin (bot)'
	git config user.email 'peterdemin@users.noreply.github.com'

.PHONY: upload
upload:  ## Push static HTML docs to GH pages
	mv docs/_build/html _docs
	touch _docs/.nojekyll
	git fetch origin gh-pages
	git checkout gh-pages
	rm -rf docs
	mv _docs docs
	git add -A docs
	git commit -m "Update static html" --no-edit

.PHONY: browser
browser:  ## Open browser to see locally built HTML docs
	open docs/_build/html/index.html

.PHONY: watch
watch: docs browser  ## compile the docs watching for changes
	watch '$(MAKE) docs'
