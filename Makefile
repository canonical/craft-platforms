PROJECT=craft_platforms
SOURCES=$(wildcard *.py) $(PROJECT) tests
DOCS=docs

ifneq ($(OS),Windows_NT)
	OS := $(shell uname)
endif
ifneq ($(shell which snap),)
	TOOL_INSTALLER := sudo $(shell which snap)
else ifneq ($(shell which brew),)
	TOOL_INSTALLER := $(shell which brew)
else
	TOOL_INSTALLER := uv
endif

.PHONY: help
help: ## Show this help.
	@printf "%-30s %s\n" "Target" "Description"
	@printf "%-30s %s\n" "------" "-----------"
	@fgrep " ## " $(MAKEFILE_LIST) | fgrep -v grep | awk -F ': .*## ' '{$$1 = sprintf("%-30s", $$1)} 1'

.PHONY: setup
setup: setup-uv setup-lint setup-test ## Set up a development environment

.PHONY: setup-precommit
setup-precommit:  ## Set up pre-commit hooks in this repository.
	uvx pre-commit install

.PHONY: format
format: format-ruff format-codespell  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-codespell lint-mypy lint-pyright lint-yaml  ## Run all linters

.PHONY: test
test: test-unit test-integration  ## Run all tests with the default python

.PHONY: docs
docs: ## Build documentation
	uv run --frozen --extra docs sphinx-build -b html -W docs docs/_build

.PHONY: docs-auto
docs-auto:  ## Build and host docs with sphinx-autobuild
	uv run --frozen --extra docs sphinx-autobuild -b html --open-browser --port=8080 --watch $(PROJECT) -W docs docs/_build

.PHONY: format-codespell
format-codespell:  ## Fix spelling issues with codespell
	codespell --toml pyproject.toml --write-changes $(SOURCES)

.PHONY: format-ruff
format-ruff:  ## Automatically format with ruff
	ruff format $(SOURCES)
	ruff check --fix $(SOURCES)

.PHONY: lint-codespell
lint-codespell: ## Check spelling with codespell
	codespell --toml pyproject.toml $(SOURCES)

.PHONY: lint-docs
lint-docs:  ## Lint the documentation
	uv run --frozen --extra docs sphinx-lint --enable all $(DOCS)

.PHONY: lint-mypy
lint-mypy: ## Check types with mypy
	uv run mypy --install-types --non-interactive $(PROJECT)

.PHONY: lint-pyright
lint-pyright: ## Check types with pyright
	uv run pyright $(SOURCES)

.PHONY: lint-ruff
lint-ruff:  ## Lint with ruff
	ruff format --diff $(SOURCES)
	ruff check $(SOURCES)

.PHONY: lint-shellcheck
lint-shellcheck:
	sh -c 'git ls-files | file --mime-type -Nnf- | grep shellscript | rev | cut -d: -f2- | rev | xargs -r shellcheck'

.PHONY: lint-yaml
lint-yaml:  ## Lint YAML files with yamllint
	yamllint .

.PHONY: test-unit
test-unit: ## Run unit tests
	uv run --frozen pytest --cov=$(PROJECT) --cov-config=pyproject.toml --cov-report=xml:.coverage.unit.xml --junit-xml=.results.unit.xml tests/unit

.PHONY: test-integration
test-integration:  ## Run integration tests
	uv run --frozen pytest --cov=$(PROJECT) --cov-config=pyproject.toml --cov-report=xml:.coverage.integration.xml --junit-xml=.results.integration.xml tests/integration

.PHONY: setup-test
setup-test: setup-uv # Set up a testing environment, without linters.
ifneq ($(shell which apt-get),)
	sudo apt-get --yes install libxml2-dev libxslt-dev
else ifneq ($(shell which brew),)
	brew install libxml2 libxslt
endif

.PHONY: setup-uv
setup-uv: # Install UV. Mostly useful as an intermediate target.
ifneq ($(shell which uv),)
else ifneq ($(shell which snap),)
	sudo snap install --classic astral-uv
else ifneq ($(shell which brew),)
	brew install uv
else
	pipx install uv
endif

.PHONY: setup-lint
setup-lint: setup-uv  # Set up the necessary linters. Mostly useful for CI
ifeq ($(shell which ruff),)
	$(TOOL_INSTALLER) install ruff
endif
ifeq ($(shell which codespell),)
	$(TOOL_INSTALLER) install codespell
endif
ifeq ($(shell which shellcheck),)
	$(TOOL_INSTALLER) install shellcheck
endif
ifeq ($(shell which yamllint),)
	uv tool install --upgrade yamllint
endif
