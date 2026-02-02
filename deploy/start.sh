#!/bin/bash
# start.sh - Start KNA History application

set -e

echo "=========================================="
echo "KNA History - Starting Application"
echo "=========================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it first:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if certificates exist
source .env
if [ ! -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo "ERROR: SSL certificates not found!"
    echo "Please run the certificate setup first:"
    echo "  ./setup-certificates.sh"
    exit 1
fi

echo "Pulling latest images..."
docker compose pull

echo "Starting services..."
docker compose up -d

echo ""
echo "✅ Application started!"
echo ""
echo "Services:"
docker compose ps

echo ""
echo "Access your application at: https://$DOMAIN_NAME"
echo ""
echo "Useful commands:"
echo "  View logs:           docker compose logs -f"
echo "  View app logs:       docker compose logs -f kna-historie"
echo "  Restart app:         docker compose restart kna-historie"
echo "  Stop all:            docker compose down"
echo "  Update and restart:  ./update.sh"
