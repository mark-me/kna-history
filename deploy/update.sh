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

# Source environment variables
source .env

# Get current version/image
echo "Current running version:"
CURRENT_IMAGE=$(docker inspect kna-historie --format='{{.Config.Image}}' 2>/dev/null || echo "not running")
CURRENT_VERSION=$(docker inspect kna-historie --format='{{index .Config.Env}}' 2>/dev/null | grep -o 'APP_VERSION=[^,]*' | cut -d'=' -f2 || echo "unknown")

echo "  Image: $CURRENT_IMAGE"
echo "  Version: $CURRENT_VERSION"

# Create backup tag of current image
if [ "$CURRENT_IMAGE" != "not running" ]; then
    echo ""
    echo "Creating backup of current image..."
    docker tag $CURRENT_IMAGE ghcr.io/mark-me/kna-history:backup-$(date +%Y%m%d-%H%M%S)
    echo "âœ… Backup created"
fi

echo ""
echo "Pulling latest image from registry..."
docker compose pull kna-historie

# Check if image actually changed
NEW_IMAGE_ID=$(docker images ghcr.io/mark-me/kna-history:latest -q)
CURRENT_IMAGE_ID=$(docker inspect kna-historie --format='{{.Image}}' 2>/dev/null | cut -d':' -f2 || echo "none")

if [ "$NEW_IMAGE_ID" = "$CURRENT_IMAGE_ID" ]; then
    echo ""
    echo "ℹ️  No new version available - already running latest image"
    read -p "Restart anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Update cancelled."
        exit 0
    fi
fi

echo ""
echo "Restarting application with new image..."
docker compose up -d kna-historie

echo ""
echo "Waiting for application to be healthy..."
RETRY_COUNT=0
MAX_RETRIES=30

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:5000/health &>/dev/null; then
        break
    fi
    echo -n "."
    sleep 2
    ((RETRY_COUNT++))
done
echo ""

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo ""
    echo "âŒ ERROR: Application failed to become healthy within 60 seconds"
    echo ""
    echo "Check logs with: docker compose logs kna-historie"
    echo ""
    echo "To rollback to previous version:"
    echo "  docker compose down kna-historie"
    echo "  docker tag ghcr.io/mark-me/kna-history:backup-* ghcr.io/mark-me/kna-history:latest"
    echo "  docker compose up -d kna-historie"
    exit 1
fi

echo ""
echo "âœ… Update completed successfully!"

NEW_VERSION=$(docker inspect kna-historie --format='{{index .Config.Env}}' | grep -o 'APP_VERSION=[^,]*' | cut -d'=' -f2 || echo "unknown")

echo ""
echo "Version update:"
echo "  From: $CURRENT_VERSION"
echo "  To:   $NEW_VERSION"

echo ""
echo "Application status:"
docker compose ps kna-historie

echo ""
echo "Recent logs:"
docker compose logs --tail=20 kna-historie

echo ""
echo "Useful commands:"
echo "  View full logs:      docker compose logs -f kna-historie"
echo "  Check health:        curl http://localhost:5000/health"
echo "  Restart if needed:   docker compose restart kna-historie"
echo ""
echo "If you experience issues, check the logs or rollback:"
echo "  docker compose logs kna-historie"
echo "  # To rollback (if needed):"
echo "  docker compose down kna-historie"
echo "  docker tag ghcr.io/mark-me/kna-history:backup-TIMESTAMP ghcr.io/mark-me/kna-history:latest"
echo "  docker compose up -d kna-historie"
