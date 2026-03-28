.PHONY: help install lint typecheck test test-cov run-% docker-build docker-up clean

PYTHON ?= python
STREAMLIT ?= streamlit

help: ## Show this help
	@grep -E '^[a-zA-Z_%-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

lint: ## Run ruff linter
	$(PYTHON) -m ruff check core/ usecases/ tests/

lint-fix: ## Auto-fix lint issues
	$(PYTHON) -m ruff check --fix core/ usecases/ tests/

typecheck: ## Run mypy type checker
	$(PYTHON) -m mypy core/

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ -v --cov=core --cov=usecases --cov-report=term-missing

# Run individual use cases: make run-rural_bank_onboarding
run-%: ## Run a use case (e.g., make run-rural_bank_onboarding)
	$(STREAMLIT) run usecases/$*/app.py

docker-build: ## Build Docker image
	docker build -f docker/Dockerfile -t sarvam-enterprise .

docker-up: ## Start all services via docker compose
	docker compose -f docker/docker-compose.yml up -d

docker-down: ## Stop all services
	docker compose -f docker/docker-compose.yml down

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
