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

# Database migration commands
db-migrate: ## Create new database migration
	@read -p "Migration message: " msg; \
	cd backend && alembic revision --autogenerate -m "$$msg"
	@echo "✅ Migration created. Review it and run 'make db-upgrade'"

db-upgrade: ## Apply database migrations
	@echo "⬆️  Applying database migrations..."
	cd backend && alembic upgrade head
	@echo "✅ Migrations applied"

db-downgrade: ## Rollback one database migration
	@echo "⬇️  Rolling back migration..."
	cd backend && alembic downgrade -1
	@echo "✅ Migration rolled back"

db-reset: ## Reset database (WARNING: deletes all data)
	@echo "⚠️  This will delete ALL data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker-compose down -v; \
		docker-compose up -d postgres redis; \
		sleep 3; \
		cd backend && alembic upgrade head; \
		echo "✅ Database reset complete"; \
	else \
		echo "❌ Cancelled"; \
	fi

# Crawler commands
crawl: ## Run all crawlers
	@echo "🕷️  Running all crawlers..."
	cd backend && python run_all_crawlers.py

# Celery commands
celery-worker: ## Start Celery worker
	@echo "👷 Starting Celery worker..."
	cd backend && celery -A celery_app worker --loglevel=info

celery-beat: ## Start Celery beat scheduler
	@echo "⏰ Starting Celery beat..."
	cd backend && celery -A celery_app beat --loglevel=info

celery-monitor: ## Start Celery Flower monitor
	@echo "📊 Starting Celery Flower..."
	cd backend && celery -A celery_app flower

# Configuration and validation
check-config: ## Validate configuration
	@echo "⚙️  Checking configuration..."
	cd backend && python -m utils.config_validator

# Code quality
format: ## Format code with black
	@echo "🎨 Formatting code..."
	cd backend && black . --line-length=100

# Quick start command
quickstart: ## Quick setup for new developers
	@echo "🚀 Quick Start for UN Jobs Hub"
	@echo ""
	@echo "1. Installing dependencies..."
	$(MAKE) install
	@echo ""
	@echo "2. Starting Docker services..."
	$(MAKE) db-up
	@sleep 5
	@echo ""
	@echo "3. Running migrations..."
	$(MAKE) db-upgrade
	@echo ""
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  - Run 'make dev' to start both servers"
	@echo "  - Visit http://localhost:3000 for frontend"
	@echo "  - Visit http://localhost:8000/docs for API docs"




