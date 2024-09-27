PROJECT=craft_platforms
SOURCES=$(wildcard *.py) $(PROJECT) tests
DOCS=docs

ifneq ($(OS),Windows_NT)
	OS := $(shell uname)
endif
SNAP_PATH := $(shell which snap)

.PHONY: help
help: ## Show this help.
	@printf "%-30s %s\n" "Target" "Description"
	@printf "%-30s %s\n" "------" "-----------"
	@fgrep " ## " $(MAKEFILE_LIST) | fgrep -v grep | awk -F ': .*## ' '{$$1 = sprintf("%-30s", $$1)} 1'

.PHONY: setup
setup: setup-tests setup-lint ## Set up a development environment
	uv tool update-shell

.PHONY: setup-tests
setup-tests: uv ## Set up an environment for tests

.PHONY: setup-lint
setup-lint: codespell ruff shellcheck yamllint ## Set up an environment for linting

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
	uv run --frozen pytest --junit-xml=.results.unit.xml tests/unit

.PHONY: coverage
coverage: ## Run unit tests with coverage
	uv run --frozen pytest --cov=$(PACKAGE) --cov-config=pyproject.toml --cov-report=xml:.coverage.xml --junit-xml=.results.unit.xml tests/unit

.PHONY: test-integration
test-integration:  ## Run integration tests
	uv run --frozen pytest --junit-xml=.results.integration.xml tests/integration


# Setups for necessary tools.
.PHONY: uv
uv:
ifneq ($(shell which uv),)
else ifeq ($(OS),Windows_NT)
		powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
else ifneq ($(shell which snap),)
	sudo snap install --classic astral-uv
else
	echo curl -LsSf https://astral.sh/uv/install.sh | sh
endif

uv_tools := codespell ruff
$(uv_tools): uv
ifneq ($(shell which $@),)
else ifneq ($(SNAP_PATH),)
	sudo snap install $@
else
	uv tool install --upgrade $@
endif

.PHONY: shellcheck
shellcheck: uv
ifneq ($(shell which shellcheck),)
else ifeq ($OS,Windows_NT)
	choco install shellcheck
else ifneq ($(SNAP_PATH),)
	sudo snap install shellcheck
else ifneq ($(shell which brew),)
	brew install shellcheck
endif

.PHONY: yamllint
yamllint:
	uv tool install --upgrade yamllint
