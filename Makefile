.DEFAULT_GOAL := help

.PHONY: help
help: ## Print help
	@grep -E '^[^.]\w+( \w+)*:.*##' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ":.*## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: venv
venv:  ## Create virtualenv
	bin/venv-update venv= -p python3 venv install= -r requirements-dev.txt -r requirements.txt
	venv/bin/pre-commit autoupdate
	venv/bin/pre-commit install

.PHONY: run
run: venv ## Run script
	venv/bin/python playlist_updates.py

.PHONY: clean
clean: ## Clean working directory
	find . -iname '*.pyc' | xargs rm -f
	rm -rf ./venv
