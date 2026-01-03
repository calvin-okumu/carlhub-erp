#!/bin/bash

# DjangoCRM Unified Setup Script
# Sets up both backend and frontend for development

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in Docker
is_docker() {
    [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]
}

# Detect environment
detect_environment() {
    if [ -n "$CI" ] || [ -n "$GITHUB_ACTIONS" ]; then
        echo "ci"
    elif [ "$NODE_ENV" = "production" ]; then
        echo "production"
    elif [ -d ".git" ]; then
        echo "development"
    else
        echo "staging"
    fi
}

# Setup backend
setup_backend() {
    log_info "Setting up Django backend..."

    if [ ! -d "backend" ]; then
        log_error "Backend directory not found!"
        exit 1
    fi

    cd backend

    # Create virtual environment if not in Docker
    if ! is_docker; then
        if [ ! -d "venv" ]; then
            log_info "Creating Python virtual environment..."
            python3 -m venv venv
        fi
        source venv/bin/activate
    fi

    # Install dependencies
    log_info "Installing Python dependencies..."
    pip install -r requirements.txt

    # Check and start Redis for caching
    if command -v redis-server &> /dev/null; then
        log_info "Starting Redis server for caching..."
        redis-server --daemonize yes 2>/dev/null || log_warning "Redis already running"
    else
        log_warning "Redis not installed. Install with: sudo apt install redis-server"
    fi

    # Setup database and application
    log_info "Running automated backend setup..."
    python manage.py setup_project

    cd ..
    log_success "Backend setup completed!"
}

# Setup frontend
setup_frontend() {
    log_info "Setting up Next.js frontend..."

    if [ ! -d "frontend" ]; then
        log_error "Frontend directory not found!"
        exit 1
    fi

    cd frontend

    # Run frontend setup script
    log_info "Running frontend setup..."
    if [ -f "scripts/setup.mjs" ]; then
        node scripts/setup.mjs
    else
        log_warning "Frontend setup script not found, running manual setup..."

        # Manual setup as fallback
        npm install
        npm run lint 2>/dev/null || log_warning "Linting failed, continuing..."
        npx tsc --noEmit 2>/dev/null || log_warning "Type checking failed, continuing..."
    fi

    cd ..
    log_success "Frontend setup completed!"
}

# Setup Docker environment
setup_docker() {
    log_info "Setting up Docker environment..."

    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed!"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed!"
        exit 1
    fi

    log_info "Starting Docker services..."
    docker-compose up -d

    log_success "Docker environment is running!"
    log_info "Services available at:"
    echo "  - Backend API: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - PostgreSQL: localhost:5432"
}

# Show usage
show_usage() {
    echo "DjangoCRM Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --backend-only     Setup only the backend"
    echo "  --frontend-only    Setup only the frontend"
    echo "  --docker           Setup Docker environment"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Setup both backend and frontend"
    echo "  $0 --docker          # Setup Docker environment"
    echo "  $0 --backend-only    # Setup only backend"
}

# Main execution
main() {
    local backend_only=false
    local frontend_only=false
    local use_docker=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backend-only)
                backend_only=true
                shift
                ;;
            --frontend-only)
                frontend_only=true
                shift
                ;;
            --docker)
                use_docker=true
                shift
                ;;
            --help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    local environment=$(detect_environment)
    log_info "Environment detected: $environment"

    # Docker setup (if requested)
    if [ "$use_docker" = true ]; then
        setup_docker
        exit 0
    fi

    # Backend setup
    if [ "$frontend_only" = false ]; then
        setup_backend
    fi

    # Frontend setup
    if [ "$backend_only" = false ]; then
        setup_frontend
    fi

    # Final success message
    log_success "🎉 DjangoCRM setup completed successfully!"
    echo ""
    log_info "Next steps:"
    if [ "$environment" = "development" ]; then
        echo "  1. Start backend: cd backend && python manage.py runserver"
        echo "  2. Start frontend: cd frontend && npm run dev"
        echo "  3. Open browser: http://localhost:3000"
    else
        echo "  1. Configure production environment variables"
        echo "  2. Run: docker-compose up -d"
        echo "  3. Access application at configured URLs"
    fi
}

# Run main function
main "$@"