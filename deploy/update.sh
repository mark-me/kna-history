#!/bin/bash
# update.sh - Update KNA History application to latest version

set -e

echo "=========================================="
echo "KNA History - Update Application"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    exit 1
fi

echo "Pulling latest images from registry..."
docker compose pull kna-historie

echo ""
echo "Current running version:"
docker inspect kna-historie --format='{{index .Config.Env}}' 2>/dev/null | grep -o 'APP_VERSION=[^,]*' || echo "Not running"

echo ""
echo "Restarting application with new image..."
docker compose up -d kna-historie

echo ""
echo "Waiting for application to be healthy..."
sleep 5

if docker compose ps kna-historie | grep -q "Up"; then
    echo ""
    echo "✅ Update completed successfully!"
    
    echo ""
    echo "New version:"
    docker inspect kna-historie --format='{{index .Config.Env}}' | grep -o 'APP_VERSION=[^,]*'
    
    echo ""
    echo "To view logs:"
    echo "  docker compose logs -f kna-historie"
else
    echo ""
    echo "❌ ERROR: Application failed to start"
    echo "Check logs with: docker compose logs kna-historie"
    exit 1
fi
