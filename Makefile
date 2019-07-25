.DEFAULT_GOAL := help

.PHONY: help
help: ## Print help
	@grep -E '^[^.]\w+( \w+)*:.*##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv:  ## Create virtualenv
	bin/venv-update \
		venv= -p python3 venv \
		install= -r requirements-dev.txt -r requirements.txt \
		bootstrap-deps= -r requirements-bootstrap.txt \
		>/dev/null
	venv/bin/pre-commit install

.PHONY: test
test: venv ## Run script
	venv/bin/mypy pynes/
	venv/bin/check-requirements
	venv/bin/coverage run -m pytest --strict tests/
	venv/bin/coverage report --fail-under 100 --omit 'tests/*'
	venv/bin/coverage report --fail-under 100 --include 'tests/*'
	venv/bin/pre-commit run --all-files

.PHONY: clean
clean: ## Clean working directory
	find . -iname '*.pyc' | xargs rm -f
	rm -rf ./venv
