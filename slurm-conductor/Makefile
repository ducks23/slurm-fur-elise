# TARGETS
lint: ## Run linter
	tox -e lint

clean: ## Remove .tox and build dirs
	rm -rf .tox/
	rm -rf venv/
	rm -rf build/

push-charm-to-edge: ## Push charm to edge s3
	@./scripts/push_charm.sh edge

pull-charm-from-edge: ## Pull nhc.charm from edge s3
	@wget https://omnivector-public-assets.s3-us-west-2.amazonaws.com/charms/nhc/edge/nhc.charm

pull-snap-from-edge: ## Pull snap from edge s3
	@./scripts/pull_snap.sh edge

# Display target comments in 'make help'
help: 
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# SETTINGS
# Use one shell for all commands in a target recipe
.ONESHELL:
# Set default goal
.DEFAULT_GOAL := help
# Use bash shell in Make instead of sh 
SHELL := /bin/bash
