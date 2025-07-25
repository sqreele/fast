#!/bin/bash

# Docker Management Script for PM System

set -e

# Detect docker compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo "Error: Neither 'docker-compose' nor 'docker compose' is available."
    exit 1
fi

show_help() {
    echo "Usage: $0 {dev|prod|stop|clean|logs|db-shell}"
    echo ""
    echo "Commands:"
    echo "  dev      - Start development environment"
    echo "  prod     - Start production environment"
    echo "  stop     - Stop all containers"
    echo "  clean    - Stop and remove all containers and volumes"
    echo "  logs     - Show logs from all services"
    echo "  db-shell - Connect to PostgreSQL database"
    echo "  help     - Show this help message"
}

case "$1" in
    dev)
        echo "Starting development environment..."
        $DOCKER_COMPOSE up --build -d
        echo "Development environment started!"
        echo "- Frontend: http://localhost:3000"
        echo "- Backend API: http://localhost:8000"
        echo "- Database Admin: http://localhost:8081"
        echo "- Nginx: http://localhost"
        ;;
    prod)
        echo "Starting production environment..."
        $DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.prod.yml up --build -d
        echo "Production environment started!"
        echo "- Application: http://localhost"
        echo "- Database Admin: http://localhost:8081"
        ;;
    stop)
        echo "Stopping all containers..."
        $DOCKER_COMPOSE down
        echo "All containers stopped."
        ;;
    clean)
        echo "Stopping and cleaning up all containers and volumes..."
        $DOCKER_COMPOSE down -v --remove-orphans
        if command -v docker &> /dev/null; then
            docker system prune -f
        fi
        echo "Cleanup completed."
        ;;
    logs)
        $DOCKER_COMPOSE logs -f
        ;;
    db-shell)
        echo "Connecting to PostgreSQL database..."
        $DOCKER_COMPOSE exec pm_postgres_db psql -U pm_user -d pm_database
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Invalid command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac