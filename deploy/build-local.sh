#!/bin/bash
# build-local.sh - Build Docker images locally for testing

set -e

VERSION=${1:-"local"}
PUSH=${2:-false}

echo "=========================================="
echo "KNA History - Local Build"
echo "=========================================="
echo "Version: $VERSION"
echo "Push to registry: $PUSH"
echo ""

# Build the app image
echo "Building application image..."
docker build \
    -t ghcr.io/mark-me/kna-history:$VERSION \
    -f app/Dockerfile \
    --build-arg APP_VERSION=$VERSION \
    ..

echo ""
echo "Building nginx image..."
docker build -t kna-history-nginx:latest -f nginx/Dockerfile nginx/

echo ""
echo "Building certbot-auto image..."
docker build -t kna-history-certbot-auto:latest -f certbot-auto/Dockerfile certbot-auto/

echo ""
echo "Building certbot-initial image..."
docker build -t kna-history-certbot-initial:latest -f certbot-initial/Dockerfile certbot-initial/

echo ""
echo "✅ Build completed!"
echo ""
echo "Built images:"
docker images | grep -E "kna-history|ghcr.io/mark-me/kna-history"

if [ "$PUSH" = "true" ] || [ "$PUSH" = "--push" ]; then
    echo ""
    echo "Pushing to registry..."
    docker push ghcr.io/mark-me/kna-history:$VERSION
    echo "✅ Pushed to registry"
fi

echo ""
echo "To test locally:"
echo "  1. Update docker-compose.yml to use: ghcr.io/mark-me/kna-history:$VERSION"
echo "  2. Run: docker compose up -d"
