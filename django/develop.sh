#!/bin/bash

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down..."

    # Stop Django dev server if running
    if [ ! -z "$DJANGO_PID" ]; then
        print_info "Stopping Django dev server (PID: $DJANGO_PID)..."
        kill $DJANGO_PID 2>/dev/null || true
        wait $DJANGO_PID 2>/dev/null || true
    fi

    # Stop Celery worker if running
    if [ ! -z "$CELERY_PID" ]; then
        print_info "Stopping Celery worker (PID: $CELERY_PID)..."
        kill $CELERY_PID 2>/dev/null || true
        wait $CELERY_PID 2>/dev/null || true
    fi

    # Stop Docker Compose services
    print_info "Stopping Docker Compose services..."
    docker compose -f docker-compose.dev.yml down

    print_info "Cleanup complete. Goodbye!"
    exit 0
}

# Trap EXIT and INT signals
trap cleanup EXIT INT TERM

# Check if docker compose is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Read .env file if it exists
if [ -r .env ]; then
    export $(grep -v '^#' .env | xargs)
    print_info "Loaded environment variables from .env"
fi

# Set default port if not specified
if [ -z ${COHIVA_DEV_PORT+x} ]; then
    COHIVA_DEV_PORT=8000
    print_info "Using default port $COHIVA_DEV_PORT (set COHIVA_DEV_PORT in .env to change)"
fi

# Parse command line arguments
START_CELERY=false
SKIP_MIGRATIONS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --celery)
            START_CELERY=true
            shift
            ;;
        --skip-migrations)
            SKIP_MIGRATIONS=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --celery           Start Celery worker alongside Django"
            echo "  --skip-migrations  Skip running migrations on startup"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

print_info "Starting Cohiva development environment..."

# Start Docker Compose services
print_info "Starting Docker Compose services (MariaDB, Redis)..."
docker compose -f docker-compose.dev.yml up -d

# Wait for services to be healthy
print_info "Waiting for services to be ready..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose -f docker-compose.dev.yml ps | grep -q "healthy"; then
        # Check if all services are healthy
        unhealthy=$(docker compose -f docker-compose.dev.yml ps --format json | grep -v "healthy" | grep "health" || true)
        if [ -z "$unhealthy" ]; then
            print_info "All services are healthy!"
            break
        fi
    fi
    sleep 2
    elapsed=$((elapsed + 2))
    echo -n "."
done
echo ""

if [ $elapsed -ge $timeout ]; then
    print_warn "Services did not become healthy within ${timeout}s, continuing anyway..."
fi

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    print_warn "No Python virtual environment is active!"
    print_warn "It's recommended to activate your virtual environment first."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run migrations unless skipped
if [ "$SKIP_MIGRATIONS" = false ]; then
    print_info "Running database migrations..."
    ./manage.py migrate
else
    print_info "Skipping migrations (--skip-migrations flag set)"
fi

# Start Celery worker if requested
if [ "$START_CELERY" = true ]; then
    print_info "Starting Celery worker..."
    ./runcelery.sh &
    CELERY_PID=$!
    print_info "Celery worker started (PID: $CELERY_PID)"
fi

# Start Django development server
print_info "Starting Django development server on port $COHIVA_DEV_PORT..."
print_info "Access the application at: http://localhost:$COHIVA_DEV_PORT/admin/"
print_info ""
print_info "Press Ctrl+C to stop all services"
print_info ""

./manage.py runserver $COHIVA_DEV_PORT &
DJANGO_PID=$!

# Wait for Django process to finish
wait $DJANGO_PID
