#!/bin/bash
# Database Migration Helper for KIKI Agent™
#
# Usage:
#   ./db_migrate.sh upgrade       # Apply all pending migrations
#   ./db_migrate.sh downgrade     # Rollback last migration
#   ./db_migrate.sh new "msg"     # Create new migration
#   ./db_migrate.sh status        # Show current status
#   ./db_migrate.sh history       # Show migration history

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if alembic is installed
if ! command -v alembic &> /dev/null; then
    error "Alembic is not installed. Run: pip install alembic"
    exit 1
fi

# Set database URL from environment or use default
export KIKI_DATABASE_URL="${KIKI_DATABASE_URL:-sqlite:///./kiki_campaigns.db}"

case "$1" in
    upgrade|up)
        info "Applying migrations to database: $KIKI_DATABASE_URL"
        alembic upgrade head
        info "✓ Database is up to date"
        ;;
    
    downgrade|down)
        warn "Rolling back last migration..."
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            alembic downgrade -1
            info "✓ Migration rolled back"
        else
            error "Rollback cancelled"
            exit 1
        fi
        ;;
    
    new|create|revision)
        if [ -z "$2" ]; then
            error "Migration message required. Usage: ./db_migrate.sh new 'description'"
            exit 1
        fi
        info "Creating new migration: $2"
        alembic revision --autogenerate -m "$2"
        warn "⚠ Review the generated migration before applying!"
        ;;
    
    status|current)
        info "Current database revision:"
        alembic current
        echo ""
        info "Latest available revision:"
        alembic heads
        ;;
    
    history|log)
        info "Migration history:"
        alembic history --verbose
        ;;
    
    stamp)
        if [ -z "$2" ]; then
            error "Revision required. Usage: ./db_migrate.sh stamp <revision>"
            exit 1
        fi
        warn "Stamping database to revision: $2"
        alembic stamp "$2"
        info "✓ Database stamped"
        ;;
    
    backup)
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        
        if [[ "$KIKI_DATABASE_URL" == sqlite* ]]; then
            DB_FILE=$(echo "$KIKI_DATABASE_URL" | sed 's|sqlite:///||')
            cp "$DB_FILE" "$BACKUP_FILE"
            info "✓ SQLite backup created: $BACKUP_FILE"
        elif [[ "$KIKI_DATABASE_URL" == postgresql* ]]; then
            pg_dump "$KIKI_DATABASE_URL" > "$BACKUP_FILE"
            info "✓ PostgreSQL backup created: $BACKUP_FILE"
        else
            error "Backup only supports SQLite and PostgreSQL"
            exit 1
        fi
        ;;
    
    reset)
        error "⚠⚠⚠ WARNING: This will DELETE ALL DATA! ⚠⚠⚠"
        read -p "Type 'DELETE EVERYTHING' to confirm: " confirm
        if [ "$confirm" = "DELETE EVERYTHING" ]; then
            alembic downgrade base
            info "All migrations rolled back"
            alembic upgrade head
            info "✓ Database reset complete"
        else
            error "Reset cancelled"
            exit 1
        fi
        ;;
    
    help|--help|-h)
        echo "KIKI Agent™ Database Migration Helper"
        echo ""
        echo "Usage: ./db_migrate.sh <command> [args]"
        echo ""
        echo "Commands:"
        echo "  upgrade, up          Apply all pending migrations"
        echo "  downgrade, down      Rollback last migration (with confirmation)"
        echo "  new, create <msg>    Create new migration from model changes"
        echo "  status, current      Show current database revision"
        echo "  history, log         Show migration history"
        echo "  stamp <revision>     Manually set database revision"
        echo "  backup               Backup database before migration"
        echo "  reset                Reset database (DANGEROUS)"
        echo "  help                 Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  KIKI_DATABASE_URL    Database connection string"
        echo ""
        echo "Examples:"
        echo "  ./db_migrate.sh upgrade"
        echo "  ./db_migrate.sh new 'Add user roles'"
        echo "  ./db_migrate.sh backup && ./db_migrate.sh upgrade"
        echo ""
        ;;
    
    *)
        error "Unknown command: $1"
        echo "Run './db_migrate.sh help' for usage information"
        exit 1
        ;;
esac
