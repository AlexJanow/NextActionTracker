# Next Action Tracker - Docker Management

.PHONY: help build up down logs clean seed test prod-build prod-up prod-down

# Default target
help:
	@echo "Next Action Tracker - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build     - Build all Docker images"
	@echo "  make up        - Start development environment"
	@echo "  make down      - Stop development environment"
	@echo "  make logs      - View logs from all services"
	@echo "  make seed      - Seed database with demo data"
	@echo "  make clean     - Remove containers, networks, and volumes"
	@echo ""
	@echo "Production:"
	@echo "  make prod-build - Build production images"
	@echo "  make prod-up    - Start production environment"
	@echo "  make prod-down  - Stop production environment"
	@echo ""
	@echo "Utilities:"
	@echo "  make test      - Run tests in containers"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"
	@echo "  make db-shell  - Connect to database"

# Development commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

seed:
	docker-compose exec backend python -m app.database.seed

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

# Production commands
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Utility commands
test:
	docker-compose exec backend python -m pytest
	docker-compose exec frontend npm test -- --run

shell-backend:
	docker-compose exec backend bash

shell-frontend:
	docker-compose exec frontend sh

db-shell:
	docker-compose exec db psql -U nat_user -d nat_dev

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health && echo "✓ Backend healthy"
	@curl -f http://localhost:3000 && echo "✓ Frontend healthy"