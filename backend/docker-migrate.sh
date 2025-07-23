#!/bin/bash

# Database Migration Script for Docker Environment
# This script runs migrations inside the Docker container

set -e

echo "🔧 PM System Database Migration Script"
echo "======================================"

# Function to run migration command
run_migration() {
    local command="$1"
    local description="$2"
    
    echo "🔄 $description..."
    
    if docker-compose exec fastapi alembic $command; then
        echo "✅ $description completed successfully"
        return 0
    else
        echo "❌ $description failed"
        return 1
    fi
}

# Check if containers are running
if ! docker-compose ps | grep -q "fastapi.*Up"; then
    echo "❌ FastAPI container is not running. Please start the services first:"
    echo "   docker-compose up -d"
    exit 1
fi

# Check if database is ready
echo "🔍 Checking database connection..."
if ! docker-compose exec fastapi python -c "
from database import engine
with engine.connect() as conn:
    conn.execute('SELECT 1')
print('Database connection successful')
"; then
    echo "❌ Database connection failed. Please ensure PostgreSQL is running."
    exit 1
fi

# Parse command line arguments
case "${1:-help}" in
    "init")
        echo "📝 Creating initial migration..."
        run_migration "revision --autogenerate -m 'Initial migration'" "Creating initial migration"
        run_migration "upgrade head" "Applying initial migration"
        ;;
    "create")
        if [ -z "$2" ]; then
            echo "❌ Please provide a migration message"
            echo "Usage: $0 create 'Your migration message'"
            exit 1
        fi
        run_migration "revision --autogenerate -m '$2'" "Creating migration: $2"
        ;;
    "upgrade")
        revision="${2:-head}"
        run_migration "upgrade $revision" "Upgrading to $revision"
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            echo "❌ Please provide a revision to downgrade to"
            echo "Usage: $0 downgrade <revision>"
            exit 1
        fi
        run_migration "downgrade $2" "Downgrading to $2"
        ;;
    "history")
        run_migration "history" "Showing migration history"
        ;;
    "current")
        run_migration "current" "Showing current revision"
        ;;
    "pending")
        run_migration "show head" "Showing pending migrations"
        ;;
    "reset")
        echo "⚠️  WARNING: This will delete all data!"
        read -p "Are you sure you want to reset the database? (yes/no): " confirm
        if [ "$confirm" != "yes" ]; then
            echo "❌ Database reset cancelled"
            exit 0
        fi
        
        echo "🗑️  Resetting database..."
        docker-compose exec fastapi python init_db.py
        run_migration "stamp head" "Stamping current revision"
        ;;
    "help"|*)
        echo "
🔧 PM System Database Migration Manager (Docker)

Usage:
  $0 <command> [options]

Commands:
  init                    - Create and apply initial migration
  create <message>        - Create new migration with message
  upgrade [revision]      - Upgrade to revision (default: head)
  downgrade <revision>    - Downgrade to revision
  history                 - Show migration history
  current                 - Show current revision
  pending                 - Show pending migrations
  reset                   - Reset database (WARNING: deletes all data)

Examples:
  $0 init
  $0 create 'Add user table'
  $0 upgrade
  $0 downgrade -1
  $0 history

Prerequisites:
  - Docker Compose services must be running
  - Database must be accessible
        "
        ;;
esac 