.PHONY: help install dev backend frontend db-up db-down clean lint test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt && playwright install chromium
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev: ## Run both frontend and backend in development mode
	docker-compose up -d postgres redis
	@echo "Starting development servers..."
	$(MAKE) -j2 backend frontend

backend: ## Run backend development server
	cd backend && uvicorn main:app --reload

frontend: ## Run frontend development server
	cd frontend && npm run dev

db-up: ## Start PostgreSQL and Redis
	docker-compose up -d postgres redis

db-down: ## Stop PostgreSQL and Redis
	docker-compose down

clean: ## Clean temporary files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	cd frontend && rm -rf .next node_modules

lint: ## Run linters
	cd backend && python -m pylint **/*.py || true
	cd frontend && npm run lint

test: ## Run all tests
	python run_tests.py

test-backend: ## Run backend tests only
	cd backend && pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing

test-frontend: ## Run frontend tests only
	cd frontend && npm run test:ci

test-unit: ## Run unit tests only
	cd backend && pytest tests/unit/ -v
	cd frontend && npm run test -- --testPathPattern=unit

test-integration: ## Run integration tests only
	cd backend && pytest tests/integration/ -v
	cd frontend && npm run test -- --testPathPattern=integration

test-coverage: ## Run tests with coverage report
	python run_tests.py --install-deps
	@echo "Coverage reports generated in backend/htmlcov/ and frontend/coverage/"

test-watch: ## Run tests in watch mode
	cd backend && pytest tests/ -v --tb=short -x
	cd frontend && npm run test:watch

test-ci: ## Run tests for CI/CD
	python run_tests.py --all --install-deps

build: ## Build production images
	docker-compose build

up: ## Start all services in production mode
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f



