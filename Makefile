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

test: ## Run tests
	cd backend && pytest
	cd frontend && npm run test

build: ## Build production images
	docker-compose build

up: ## Start all services in production mode
	docker-compose up -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs from all services
	docker-compose logs -f



