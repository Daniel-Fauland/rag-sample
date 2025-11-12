.PHONY: help setup env-check db-start db-stop db-restart db-logs db-migrate db-migrate-down db-migrate-history db-clean redis-cli postgres-cli run run-docker test test-file clean stop install-uv check-docker

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Helper to find uv executable (checks PATH, then common installation locations)
# This ensures uv works even if it was just installed and not yet in PATH
# Usage: UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); $$UV_CMD

help: ## Show this help message
	@echo "$(CYAN)Available commands:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ============================================================================
# Setup Commands
# ============================================================================

setup: env-check install-uv env-setup db-start db-wait db-migrate ## Complete initial setup (install uv, create .env, start DBs, run migrations)
	@echo "$(GREEN)✓ Setup complete! You can now run 'make run' to start the backend$(NC)"

install-uv: ## Install uv package manager if not already installed
	@if command -v uv >/dev/null 2>&1; then \
		echo "$(GREEN)✓ uv is already installed$(NC)"; \
	else \
		echo "$(YELLOW)Installing uv...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		UV_PATH=""; \
		if [ -f "$$HOME/.local/bin/uv" ]; then \
			UV_PATH="$$HOME/.local/bin"; \
		elif [ -f "$$HOME/.cargo/bin/uv" ]; then \
			UV_PATH="$$HOME/.cargo/bin"; \
		fi; \
		if [ -n "$$UV_PATH" ]; then \
			export PATH="$$UV_PATH:$$PATH"; \
			if command -v uv >/dev/null 2>&1; then \
				echo "$(GREEN)✓ uv installed successfully and available in current session$(NC)"; \
			else \
				echo "$(YELLOW)⚠ uv installed but not in PATH. Please restart your shell or run: export PATH=\"$$UV_PATH:\$$PATH\"$(NC)"; \
			fi; \
		else \
			echo "$(YELLOW)⚠ uv installation completed, but location not detected. Please restart your shell.$(NC)"; \
		fi; \
	fi

check-docker: ## Check if Docker is installed and running
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "$(RED)✗ Docker is not installed. Please install Docker first.$(NC)"; \
		exit 1; \
	fi
	@if ! docker info >/dev/null 2>&1; then \
		echo "$(RED)✗ Docker is not running. Please start Docker.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓ Docker is installed and running$(NC)"

env-check: check-docker ## Check if all required tools are available
	@echo "$(CYAN)Checking prerequisites...$(NC)"

env-setup: ## Create .env file from example if it doesn't exist
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ Created .env$(NC)"; \
		echo "$(YELLOW)⚠ Please update .env with your JWT_SECRET and other credentials if needed$(NC)"; \
	else \
		echo "$(GREEN)✓ .env already exists$(NC)"; \
	fi

# ============================================================================
# Database Commands
# ============================================================================

db-start: check-docker ## Start Postgres and Redis databases
	@echo "$(CYAN)Starting databases...$(NC)"
	@docker compose up -d postgres redis
	@echo "$(GREEN)✓ Databases started$(NC)"

db-stop: ## Stop databases without removing containers
	@echo "$(CYAN)Stopping databases...$(NC)"
	@docker compose stop postgres redis
	@echo "$(GREEN)✓ Databases stopped$(NC)"

db-restart: db-stop db-start ## Restart databases

db-logs: ## Show database logs (use CTRL+C to exit)
	@docker compose logs -f postgres redis

db-wait: ## Wait for databases to be healthy
	@echo "$(CYAN)Waiting for databases to be ready...$(NC)"
	@timeout=60; \
	elapsed=0; \
	while [ $$elapsed -lt $$timeout ]; do \
		if docker compose ps postgres | grep -q "healthy" && docker compose ps redis | grep -q "healthy"; then \
			echo "$(GREEN)✓ Databases are ready$(NC)"; \
			exit 0; \
		fi; \
		echo "$(YELLOW)Waiting for databases... ($$elapsed/$$timeout seconds)$(NC)"; \
		sleep 2; \
		elapsed=$$((elapsed + 2)); \
	done; \
	echo "$(RED)✗ Databases failed to become healthy within $$timeout seconds$(NC)"; \
	exit 1

db-status: ## Show database container status
	@docker compose ps postgres redis

db-migrate: ## Run all database migrations (upgrade to latest)
	@echo "$(CYAN)Running database migrations...$(NC)"
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-migrate-down: ## Rollback all database migrations
	@echo "$(YELLOW)Rolling back all migrations...$(NC)"
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run alembic downgrade base
	@echo "$(GREEN)✓ Rollback complete$(NC)"

db-migrate-history: ## Show migration history
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run alembic history

db-migrate-create: ## Create a new migration (use MSG="your message")
	@if [ -z "$(MSG)" ]; then \
		echo "$(RED)✗ Please provide a message: make db-migrate-create MSG='your message'$(NC)"; \
		exit 1; \
	fi
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ Migration created$(NC)"

db-clean: ## Remove database volumes and containers (WARNING: deletes all data!)
	@echo "$(RED)⚠ This will delete all database data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker compose down -v postgres redis; \
		echo "$(GREEN)✓ Database volumes removed$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

# Database CLI access
postgres-cli: ## Access Postgres CLI (psql)
	@. .env 2>/dev/null || true; \
	DB_USER=$${DB_USER:-systemuser}; \
	DB_NAME=$${DB_NAME:-postgres}; \
	docker exec -it db-be-pg psql -U $$DB_USER -d $$DB_NAME

redis-cli: ## Access Redis CLI
	@. .env 2>/dev/null || true; \
	REDIS_PASSWORD=$${REDIS_PASSWORD:-mysecretpassword}; \
	docker exec -it db-be-redis redis-cli -a $$REDIS_PASSWORD

# ============================================================================
# Application Commands
# ============================================================================

run: ## Run FastAPI backend locally (databases must be running)
	@echo "$(CYAN)Starting FastAPI backend...$(NC)"
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run main.py

run-docker: check-docker ## Run entire stack in Docker (backend + databases)
	@echo "$(CYAN)Starting entire stack in Docker...$(NC)"
	@docker compose up --build
	@echo "$(GREEN)✓ Stack running at http://localhost:8000$(NC)"

run-docker-bg: check-docker ## Run entire stack in Docker in background
	@echo "$(CYAN)Starting entire stack in Docker (background)...$(NC)"
	@docker compose up --build -d
	@echo "$(GREEN)✓ Stack running at http://localhost:8000$(NC)"

stop: ## Stop all running containers
	@echo "$(CYAN)Stopping all containers...$(NC)"
	@docker compose down
	@echo "$(GREEN)✓ All containers stopped$(NC)"

# ============================================================================
# Testing Commands
# ============================================================================

test: ## Run all tests
	@echo "$(CYAN)Running all tests...$(NC)"
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run tests/run_tests.py

test-file: ## Run specific test file (use FILE=path/to/test.py)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)✗ Please provide a file: make test-file FILE=tests/users/test_users.py$(NC)"; \
		exit 1; \
	fi
	@echo "$(CYAN)Running tests in $(FILE)...$(NC)"
	@UV_CMD=$$(command -v uv 2>/dev/null || ([ -f "$$HOME/.local/bin/uv" ] && echo "$$HOME/.local/bin/uv") || ([ -f "$$HOME/.cargo/bin/uv" ] && echo "$$HOME/.cargo/bin/uv") || echo "uv"); \
	$$UV_CMD run tests/run_tests.py $(FILE)

# ============================================================================
# Utility Commands
# ============================================================================

clean: stop ## Clean up everything (containers, volumes, cache files)
	@echo "$(RED)⚠ This will delete all database data and clean up containers!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(CYAN)Cleaning up...$(NC)"; \
		docker compose down -v; \
		find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true; \
		find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true; \
		find . -type f -name "*.pyc" -delete 2>/dev/null || true; \
		echo "$(GREEN)✓ Cleanup complete$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

logs: ## Show logs from all Docker containers
	@docker compose logs -f

dev: db-start db-wait ## Quick start for development (start DBs and run backend locally)
	@echo "$(GREEN)✓ Databases started$(NC)"
	@echo "$(CYAN)Run 'make run' in another terminal to start the backend$(NC)"

# Quick restart of everything
restart: stop setup run ## Full restart (stop everything, setup, and run)
