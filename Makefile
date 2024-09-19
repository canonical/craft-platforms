SOURCES=$(wildcard *.py) craft_platforms tests
DOCS=docs

.PHONY: help
help: ## Show this help.
	@printf "%-30s %s\n" "Target" "Description"
	@printf "%-30s %s\n" "------" "-----------"
	@fgrep " ## " $(MAKEFILE_LIST) | fgrep -v grep | awk -F ': .*## ' '{$$1 = sprintf("%-30s", $$1)} 1'

.PHONY: snap-tools
snap-tools: start-snap-install finish-snap-install  ## Install necessary tools using snap

.PHONY: setup-precommit
setup-precommit:  ## Set up pre-commit hooks in this repository.
	uvx pre-commit install

.PHONY: autoformat
autoformat: format-ruff format-codespell  ## Run all automatic formatters

.PHONY: lint
lint: lint-ruff lint-codespell lint-mypy lint-pyright lint-yaml  ## Run all linters

.PHONY: test
test: test-unit test-integration  ## Run all tests with the default python

.PHONY: docs
docs: ## Build documentation
	uv run --extra docs sphinx-build -b html -W docs docs/_build

.PHONY: docs-auto
docs-auto:  ## Build and host docs with sphinx-autobuild
	uv run --extra docs sphinx-autobuild -b html --open-browser --port=8080 --watch craft_platforms -W docs docs/_build

.PHONY: format-codespell
format-codespell:  ## Fix spelling issues with codespell
	uv run codespell --toml pyproject.toml --write-changes $(SOURCES)

.PHONY: format-ruff
format-ruff:  ## Automatically format with ruff
	ruff format $(SOURCES)
	ruff check --fix $(SOURCES)

.PHONY: lint-codespell
lint-codespell: ## Check spelling with codespell
	uv run codespell --toml pyproject.toml $(SOURCES)

.PHONY: lint-docs
lint-docs:  ## Lint the documentation
	uv run --extra docs sphinx-lint --max-line-length 80 --enable all $(DOCS)

.PHONY: lint-mypy
lint-mypy: ## Check types with mypy
	uv run mypy --install-types --non-interactive craft_platforms

.PHONY: lint-pyright
lint-pyright: ## Check types with pyright
	uv run pyright

.PHONY: lint-ruff
lint-ruff:  ## Lint with ruff
	ruff format --diff $(SOURCES)
	ruff check $(SOURCES)

.PHONY: lint-shellcheck
lint-shellcheck:
	sh -c 'git ls-files | file --mime-type -Nnf- | grep shellscript | cut -f1 -d: | xargs -r shellcheck'

.PHONY: lint-yaml
lint-yaml:  ## Lint YAML files with yamllint
	uv run yamllint .

.PHONY: test-unit
test-unit: ## Run unit tests
	uv run pytest --cov=craft_platforms --cov-config=pyproject.toml --cov-report=xml:.coverage.unit.xml --junit-xml=.results.unit.xml tests/unit

.PHONY: test-integration
test-integration:  ## Run integration tests
	uv run pytest --cov=craft_platforms --cov-config=pyproject.toml --cov-report=xml:.coverage.integration.xml --junit-xml=.results.integration.xml tests/integration

.PHONY: start-snap-install
start-snap-install:
	snap install --no-wait codespell
	snap install --no-wait ruff
	snap install --no-wait shellcheck
	snap install --no-wait --classic astral-uv --beta

.PHONY: finish-snap-install
finish-snap-install:
	snap watch --last=install
	snap alias astral-uv.uv uv
	snap alias astral-uv.uvx uvx
