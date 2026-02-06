#!/bin/bash
# start.sh - Start KNA History application

set -e

echo "=========================================="
echo "KNA History - Starting Application"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy env.example to .env and configure it first:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

# Source environment variables
source .env

# Validate required environment variables
echo "Validating configuration..."
REQUIRED_VARS=(
    "SECRET_KEY"
    "MARIADB_PASSWORD"
    "MARIADB_ROOT_PASSWORD"
    "DATABASE_URL"
    "ADMIN_PASSWORD"
    "DOMAIN_NAME"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "ERROR: Missing required environment variables:"
    printf '  - %s\n' "${MISSING_VARS[@]}"
    echo ""
    echo "Please update your .env file with these values."
    exit 1
fi

# Check for default/insecure values
echo "Checking for default passwords..."
WARNINGS=()

if [[ "$SECRET_KEY" == *"change-this"* ]] || [[ "$SECRET_KEY" == *"your-secret"* ]]; then
    WARNINGS+=("SECRET_KEY appears to use a default value - generate a secure random key!")
fi

if [[ "$ADMIN_PASSWORD" == "admin2026!" ]] || [[ "$ADMIN_PASSWORD" == *"change"* ]]; then
    WARNINGS+=("ADMIN_PASSWORD appears to use a default value - use a strong password!")
fi

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "WARNING: Security issues detected:"
    printf '  - %s\n' "${WARNINGS[@]}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Please update your .env file with secure values."
        exit 0
    fi
fi

# Check if certificates exist
if [ ! -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo "WARNING: SSL certificates not found at /data/certbot/conf/live/$DOMAIN_NAME"
    echo "Please run the certificate setup first:"
    echo "  ./setup-certificates.sh"
    echo ""
    read -p "Continue without SSL? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if data directories exist
echo "Checking data directories..."
if [ ! -d "$DIR_RESOURCES_HOST" ]; then
    echo "WARNING: Resources directory not found: $DIR_RESOURCES_HOST"
    read -p "Create directory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo mkdir -p "$DIR_RESOURCES_HOST"
        sudo chown -R 1000:1000 "$DIR_RESOURCES_HOST"
        echo "Created: $DIR_RESOURCES_HOST"
    fi
fi

if [ ! -d "$DIR_MARIADB" ]; then
    echo "WARNING: MariaDB directory not found: $DIR_MARIADB"
    read -p "Create directory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo mkdir -p "$DIR_MARIADB"
        sudo chown -R 999:999 "$DIR_MARIADB"  # MariaDB runs as uid 999
        echo "Created: $DIR_MARIADB"
    fi
fi

echo ""
echo "Configuration summary:"
echo "  Environment:    ${FLASK_ENV:-production}"
echo "  Domain:         $DOMAIN_NAME"
echo "  MariaDB Host:   ${MARIADB_HOST:-mariadb}"
echo "  Resources:      $DIR_RESOURCES_HOST → $DIR_RESOURCES"
echo "  Database Data:  $DIR_MARIADB"
echo ""

echo "Pulling latest images..."
docker compose pull

echo ""
echo "Starting services..."
docker compose up -d

echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Check service status
echo ""
echo "Service status:"
docker compose ps

# Check application health
echo ""
echo "Checking application health..."
sleep 10
if curl -f http://localhost:5000/health &>/dev/null; then
    echo "âœ… Application is healthy!"
else
    echo "âš  Application health check failed (this might be normal if it's still starting)"
fi

echo ""
echo "âœ… Application started!"
echo ""
echo "Access your application at: https://$DOMAIN_NAME"
echo ""
echo "Useful commands:"
echo "  View logs:           docker compose logs -f"
echo "  View app logs:       docker compose logs -f kna-historie"
echo "  Restart app:         docker compose restart kna-historie"
echo "  Stop all:            docker compose down"
echo "  Update and restart:  ./update.sh"
echo "  Check health:        curl http://localhost:5000/health"
