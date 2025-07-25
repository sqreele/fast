# Docker PM System - Makefile for easy management
.PHONY: help build up down logs clean restart dev prod backup restore test lint format

# Default environment
ENV ?= development

# Help command
help: ## Show this help message
	@echo 'Usage: make [command]'
	@echo ''
	@echo 'Available commands:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Development commands
dev: ## Start development environment
	@echo "Starting development environment..."
	docker-compose up -d
	@echo "Development environment started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "Admin: http://localhost:8081"
	@echo "Logs: make logs"

dev-build: ## Build and start development environment
	@echo "Building and starting development environment..."
	docker-compose up -d --build
	@echo "Development environment built and started!"

dev-logs: ## Show development logs
	docker-compose logs -f

dev-down: ## Stop development environment
	@echo "Stopping development environment..."
	docker-compose down
	@echo "Development environment stopped!"

dev-clean: ## Stop and remove development containers, networks, and volumes
	@echo "Cleaning up development environment..."
	docker-compose down -v --remove-orphans
	docker system prune -f
	@echo "Development environment cleaned!"

# Production commands
prod: ## Start production environment
	@echo "Starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "Production environment started!"

prod-build: ## Build and start production environment
	@echo "Building and starting production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
	@echo "Production environment built and started!"

prod-logs: ## Show production logs
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f

prod-down: ## Stop production environment
	@echo "Stopping production environment..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
	@echo "Production environment stopped!"

# General commands
build: ## Build all containers
	@echo "Building all containers..."
	docker-compose build --parallel

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	@echo "Restarting all services..."
	docker-compose restart
	@echo "All services restarted!"

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show FastAPI logs
	docker-compose logs -f fastapi

logs-frontend: ## Show Next.js logs
	docker-compose logs -f frontend

logs-nginx: ## Show Nginx logs
	docker-compose logs -f nginx

logs-db: ## Show PostgreSQL logs
	docker-compose logs -f pm_postgres_db

# Database commands
db-shell: ## Access PostgreSQL shell
	docker-compose exec pm_postgres_db psql -U pm_user -d pm_database

db-backup: ## Create database backup
	@echo "Creating database backup..."
	mkdir -p ./backups
	docker-compose exec pm_postgres_db pg_dump -U pm_user -d pm_database > ./backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created in ./backups/"

db-restore: ## Restore database from backup (usage: make db-restore BACKUP=backup_file.sql)
	@if [ -z "$(BACKUP)" ]; then echo "Usage: make db-restore BACKUP=backup_file.sql"; exit 1; fi
	@echo "Restoring database from $(BACKUP)..."
	docker-compose exec -T pm_postgres_db psql -U pm_user -d pm_database < ./backups/$(BACKUP)
	@echo "Database restored from $(BACKUP)!"

# Development tools
shell-api: ## Access FastAPI container shell
	docker-compose exec fastapi bash

shell-frontend: ## Access Next.js container shell
	docker-compose exec frontend sh

shell-nginx: ## Access Nginx container shell
	docker-compose exec nginx sh

# Testing and quality
test: ## Run backend tests
	@echo "Running backend tests..."
	docker-compose exec fastapi pytest
	@echo "Backend tests completed!"

test-frontend: ## Run frontend tests
	@echo "Running frontend tests..."
	docker-compose exec frontend npm test
	@echo "Frontend tests completed!"

lint: ## Run linting for backend
	@echo "Running backend linting..."
	docker-compose exec fastapi black . --check
	docker-compose exec fastapi isort . --check-only
	docker-compose exec fastapi flake8 .
	@echo "Backend linting completed!"

format: ## Format backend code
	@echo "Formatting backend code..."
	docker-compose exec fastapi black .
	docker-compose exec fastapi isort .
	@echo "Backend code formatted!"

# Monitoring
monitoring: ## Start monitoring stack (Prometheus + Grafana)
	@echo "Starting monitoring stack..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d prometheus grafana
	@echo "Monitoring stack started!"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001 (admin/admin)"

# Security
security-scan: ## Run security scan on containers
	@echo "Running security scan..."
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image --severity HIGH,CRITICAL \
		$(shell docker-compose config --services | head -1)

# Maintenance
clean: ## Clean up unused Docker resources
	@echo "Cleaning up unused Docker resources..."
	docker system prune -af --volumes
	@echo "Cleanup completed!"

update: ## Update all containers to latest versions
	@echo "Updating all containers..."
	docker-compose pull
	docker-compose up -d --build
	@echo "All containers updated!"

# Health checks
health: ## Check health of all services
	@echo "Checking service health..."
	@docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

status: ## Show status of all services
	docker-compose ps

# SSL Certificate management (for production)
ssl-cert: ## Generate self-signed SSL certificates
	@echo "Generating self-signed SSL certificates..."
	mkdir -p ./nginx/ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout ./nginx/ssl/key.pem \
		-out ./nginx/ssl/cert.pem \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
	@echo "SSL certificates generated in ./nginx/ssl/"

# Environment setup
setup: ## Initial setup for development
	@echo "Setting up development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	@echo "Run 'make dev' to start development environment"

# Quick commands
quick-start: setup dev ## Quick start development environment
	@echo "Development environment is ready!"

quick-prod: ssl-cert prod ## Quick start production environment
	@echo "Production environment is ready!"