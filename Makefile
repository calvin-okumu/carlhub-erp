# DjangoCRM Project Makefile
# Unified commands for development, testing, and deployment

.PHONY: help setup setup-backend setup-frontend setup-docker dev dev-backend dev-frontend check-servers stop test test-backend test-frontend build build-backend build-frontend clean clean-backend clean-frontend docker-up docker-down docker-up-staging docker-down-staging docker-logs install migrate createsuperuser shell dbshell env-check db-backup db-restore ci-setup ci-test ci-build

# Default target
help:
	@echo "DjangoCRM Project Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup              - Setup both backend and frontend"
	@echo "  make setup-backend      - Setup only backend"
	@echo "  make setup-frontend     - Setup only frontend"
	@echo "  make setup-docker       - Setup Docker environment"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev                - Start both backend and frontend in development"
	@echo "  make dev-backend        - Start backend development server"
	@echo "  make dev-frontend       - Start frontend development server"
	@echo "  make check-servers      - Check if backend and frontend are accessible"
	@echo "  make stop               - Stop all development servers"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test               - Run all tests"
	@echo "  make test-backend       - Run backend tests"
	@echo "  make test-frontend      - Run frontend tests"
	@echo ""
	@echo "Build Commands:"
	@echo "  make build              - Build both backend and frontend"
	@echo "  make build-backend      - Build backend"
	@echo "  make build-frontend     - Build frontend"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make docker-up          - Start development Docker services"
	@echo "  make docker-down        - Stop development Docker services"
	@echo "  make docker-up-staging  - Start staging Docker services"
	@echo "  make docker-down-staging - Stop staging Docker services"
	@echo "  make docker-logs        - Show Docker logs"
	@echo ""
	@echo "Cleanup Commands:"
	@echo "  make clean              - Clean all build artifacts"
	@echo "  make clean-backend      - Clean backend artifacts"
	@echo "  make clean-frontend     - Clean frontend artifacts"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make install            - Install all dependencies"
	@echo "  make migrate            - Run database migrations"
	@echo "  make createsuperuser    - Create Django superuser"
	@echo "  make shell              - Open Django shell"
	@echo "  make dbshell            - Open database shell"
	@echo ""
	@echo "Environment Management:"
	@echo "  make env-check          - Check environment configuration"
	@echo ""
	@echo "Database Management:"
	@echo "  make db-backup          - Backup database"
	@echo "  make db-restore         - Restore database from latest backup"
	@echo ""
	@echo "CI/CD Commands:"
	@echo "  make ci-setup           - Setup for CI environment"
	@echo "  make ci-test            - Run CI tests"
	@echo "  make ci-build           - Run CI build"
	@echo ""
	@echo "Docker Troubleshooting:"
	@echo "  make docker-troubleshoot - Show troubleshooting guide"
	@echo "  make docker-status       - Check service status"
	@echo "  make docker-logs-all    - View recent logs from all services"
	@echo "  make docker-networks    - Inspect Docker networks"
	@echo "  make docker-connectivity - Test inter-service connectivity"
	@echo "  make docker-resources   - Show resource usage"
	@echo "  make docker-clean       - Clean up containers and volumes"
	@echo "  make docker-restart     - Restart all services"
	@echo "  make docker-rebuild     - Rebuild and restart services"

# Setup commands
setup:
	@echo "Setting up DjangoCRM (backend + frontend)..."
	@./setup.sh

setup-backend:
	@echo "Setting up backend..."
	@./setup.sh --backend-only

setup-frontend:
	@echo "Setting up frontend..."
	@./setup.sh --frontend-only

setup-docker:
	@echo "Setting up Docker environment..."
	@./setup.sh --docker

# Development commands
dev:
	@echo "Starting development environment..."
	@echo "Checking port availability..."
	@if ss -tulpn | grep -q :8000; then \
		echo "Port 8000 is in use by:"; \
		ss -tulpn | grep :8000; \
		echo "Run 'make stop' to free ports."; \
		exit 1; \
	fi
	@if ss -tulpn | grep -q :3000; then \
		echo "Port 3000 is in use by:"; \
		ss -tulpn | grep :3000; \
		echo "Run 'make stop' to free ports."; \
		exit 1; \
	fi
	@echo "Ports available. Starting servers..."
	@echo "Backend will be available at: http://localhost:8000"
	@echo "Frontend will be available at: http://localhost:3000"
	@echo ""
	@echo "Starting Redis..."
	@redis-server --daemonize yes 2>/dev/null || echo "Redis already running or not installed"
	@echo "Preparing backend environment..."
	@cd backend && . venv/bin/activate && python manage.py migrate
	@echo "Starting backend..."
	@cd backend && (. venv/bin/activate && python manage.py runserver 0.0.0.0:8000 & echo "Backend started with PID $$!")
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "Starting frontend..."
	@cd frontend && (npm run dev -- -p 3000 & echo "Frontend started with PID $$!")
	@echo ""
	@sleep 5
	@echo "Verifying server availability..."
	@curl -s http://localhost:8000 >/dev/null && echo "✅ Backend available at http://localhost:8000" || echo "⚠️  Backend not responding on http://localhost:8000"
	@curl -s http://localhost:3000 >/dev/null && echo "✅ Frontend available at http://localhost:3000" || echo "⚠️  Frontend not responding on http://localhost:3000"
	@redis-cli ping >/dev/null 2>&1 && echo "✅ Redis available" || echo "⚠️  Redis not responding"
	@echo ""
	@echo "Development servers started. Use 'make stop' to stop."

dev-backend:
	@echo "Starting backend development server..."
	@cd backend && . venv/bin/activate && python manage.py runserver

dev-frontend:
	@echo "Starting frontend development server..."
	@cd frontend && npm run dev

check-servers:
	@echo "Checking server availability..."
	@curl -s http://localhost:8000 >/dev/null && echo "✅ Backend: http://localhost:8000" || echo "❌ Backend: http://localhost:8000 (not responding)"
	@curl -s http://localhost:3000 >/dev/null && echo "✅ Frontend: http://localhost:3000" || echo "❌ Frontend: http://localhost:3000 (not responding)"
	@redis-cli ping >/dev/null 2>&1 && echo "✅ Redis: available" || echo "❌ Redis: not responding"

stop:
	@echo "Stopping development servers..."
	@echo "Stopping backend processes..."
	@ps aux | grep "runserver" | grep -v grep | awk '{print $$2}' | xargs kill 2>/dev/null && echo "Backend processes stopped" || echo "No backend processes found"
	@echo "Stopping frontend processes..."
	@ps aux | grep "npm run dev" | grep -v grep | awk '{print $$2}' | xargs kill 2>/dev/null && echo "NPM dev processes stopped" || echo "No NPM dev processes found"
	@ps aux | grep "next" | grep -v grep | awk '{print $$2}' | xargs kill 2>/dev/null && echo "Next.js processes stopped" || echo "No Next.js processes found"
	@echo "Stopping Redis processes..."
	@ps aux | grep "redis-server" | grep -v grep | awk '{print $$2}' | xargs kill 2>/dev/null && echo "Redis processes stopped" || echo "No Redis processes found"
	@echo "Verifying servers are stopped..."
	@sleep 2
	@curl -s --max-time 5 http://localhost:8000 >/dev/null && echo "⚠️  Backend still responding on http://localhost:8000" || echo "✅ Backend stopped"
	@curl -s --max-time 5 http://localhost:3000 >/dev/null && echo "⚠️  Frontend still responding on http://localhost:3000" || echo "✅ Frontend stopped"
	@ps aux | grep "redis-server" | grep -v grep >/dev/null && echo "⚠️  Redis still running" || echo "✅ Redis stopped"
	@echo "Development servers stopped."

# Testing commands
test:
	@echo "Running all tests..."
	@echo "Backend tests:" && make test-backend
	@echo "Frontend tests:" && make test-frontend

test-backend:
	@echo "Running backend tests..."
	@cd backend && . venv/bin/activate && python manage.py test

test-frontend:
	@echo "Running frontend tests..."
	@cd frontend && npm test 2>/dev/null || echo "No test script configured for frontend"

# Build commands
build:
	@echo "Building both backend and frontend..."
	@make build-backend
	@make build-frontend

build-backend:
	@echo "Building backend..."
	@cd backend && . venv/bin/activate && python manage.py collectstatic --noinput

build-frontend:
	@echo "Building frontend..."
	@cd frontend && npm run build

# Docker commands
docker-up:
	@echo "Starting development Docker services..."
	@docker compose up -d
	@echo "Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Backend: http://localhost:8000"
	@echo "  - Frontend: http://localhost:3000"

docker-down:
	@echo "Stopping Docker services..."
	@docker compose down

docker-up-staging:
	@echo "Starting staging Docker services..."
	@docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
	@echo "Staging services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - Backend: http://localhost:8000"
	@echo "  - Frontend: http://localhost:80"

docker-down-staging:
	@echo "Stopping staging Docker services..."
	@docker compose -f docker-compose.yml -f docker-compose.staging.yml down

docker-logs:
	@echo "Showing Docker logs..."
	@docker-compose logs -f

# Cleanup commands
clean:
	@echo "Cleaning all build artifacts..."
	@make clean-backend
	@make clean-frontend
	@echo "Removing Python cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

clean-backend:
	@echo "Cleaning backend artifacts..."
	@cd backend && rm -rf staticfiles/ media/ *.log
	@cd backend && find . -name "*.pyc" -delete
	@cd backend && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

clean-frontend:
	@echo "Cleaning frontend artifacts..."
	@cd frontend && rm -rf .next/ out/ node_modules/.cache
	@cd frontend && npm cache clean --force 2>/dev/null || true

# Utility commands
install:
	@echo "Installing all dependencies..."
	@pip install -r backend/requirements.txt
	@cd frontend && npm install

migrate:
	@echo "Running database migrations..."
	@cd backend && . venv/bin/activate && python manage.py migrate

createsuperuser:
	@echo "Creating Django superuser..."
	@cd backend && . venv/bin/activate && python manage.py createsuperuser

shell:
	@echo "Opening Django shell..."
	@cd backend && . venv/bin/activate && python manage.py shell

dbshell:
	@echo "Opening database shell..."
	@cd backend && . venv/bin/activate && python manage.py dbshell

# Environment management
env-check:
	@echo "Checking environment configuration..."
	@cd backend && . venv/bin/activate && python check_env.py

# Database management
db-backup:
	@echo "Backing up database..."
	@cd backend && . venv/bin/activate && python manage.py dumpdata --natural-foreign --natural-primary > db_backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "Backup completed: db_backup_$(shell date +%Y%m%d_%H%M%S).json"

db-restore:
	@echo "Restoring database from latest backup..."
	@cd backend && . venv/bin/activate && python manage.py flush --no-input && python manage.py loaddata $$(ls -t backend/db_backup_*.json | head -1)
	@echo "Database restored from latest backup"

# CI/CD commands
ci-setup:
	@echo "Setting up for CI environment..."
	@make setup-backend
	@make setup-frontend

ci-test:
	@echo "Running CI tests..."
	@make test-backend
	@make test-frontend

ci-build:
	@echo "Running CI build..."
	@make build-backend
	@make build-frontend

# Docker Troubleshooting commands
docker-troubleshoot:
	@echo "Docker Troubleshooting Guide"
	@echo "==========================="
	@echo "1. Check service status: make docker-status"
	@echo "2. View logs: make docker-logs-all"
	@echo "3. Check networks: make docker-networks"
	@echo "4. Test connectivity: make docker-connectivity"
	@echo "5. Check resource usage: make docker-resources"
	@echo "6. Clean up: make docker-clean"

docker-status:
	@echo "Service Status:"
	@docker compose ps

docker-logs-all:
	@echo "All Service Logs (last 50 lines each):"
	@echo "======================================"
	@echo "DB Logs:"
	@docker compose logs db --tail=50
	@echo ""
	@echo "Redis Logs:"
	@docker compose logs redis --tail=50
	@echo ""
	@echo "Backend Logs:"
	@docker compose logs backend --tail=50
	@echo ""
	@echo "Frontend Logs:"
	@docker compose logs frontend --tail=50

docker-networks:
	@echo "Docker Networks:"
	@docker network ls | grep django
	@echo ""
	@echo "Network Details:"
	@docker network inspect django_frontend
	@docker network inspect django_backend

docker-connectivity:
	@echo "Testing Service Connectivity:"
	@echo "============================"
	@echo "Backend health:"
	@docker compose exec backend curl -f http://localhost:8000/api/health/ || echo "Backend not responding"
	@echo ""
	@echo "Database connectivity:"
	@docker compose exec backend python manage.py dbshell -c "SELECT 1;" 2>/dev/null && echo "Database connected" || echo "Database connection failed"
	@echo ""
	@echo "Redis connectivity:"
	@docker compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379, db=0); r.ping(); print('Redis connected')" 2>/dev/null || echo "Redis connection failed"
	@echo ""
	@echo "Frontend connectivity:"
	@docker compose exec frontend curl -f http://localhost:3000 2>/dev/null && echo "Frontend responding" || echo "Frontend not responding"

docker-resources:
	@echo "Resource Usage:"
	@docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

docker-clean:
	@echo "Cleaning up Docker resources..."
	@docker compose down -v
	@docker system prune -f
	@echo "Cleanup complete. Run 'make docker-up' to restart."

docker-restart:
	@echo "Restarting all services..."
	@docker compose restart

docker-rebuild:
	@echo "Rebuilding and restarting services..."
	@docker compose down
	@docker compose build --no-cache
	@docker compose up -d