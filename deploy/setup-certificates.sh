#!/bin/bash
# setup-certificates.sh - Initial SSL certificate setup
# Run this script ONCE on first deployment to obtain SSL certificates

set -e

echo "=========================================="
echo "KNA History - Initial Certificate Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please copy .env.example to .env and configure it first:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Source environment variables
source .env

echo "Domain: $DOMAIN_NAME"
echo "Email: $EMAIL_ADDRESS"
echo ""
echo "This will:"
echo "  1. Stop any running services on port 80"
echo "  2. Run certbot in standalone mode to obtain certificates"
echo "  3. Store certificates in /data/certbot/conf"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Stop main services if running
echo "Stopping main services (if running)..."
docker compose down 2>/dev/null || true

# Run certbot initial
echo "Running certbot to obtain certificates..."
docker compose -f docker-compose.certbot-initial.yml up --build

# Check if certificates were created
if [ -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo ""
    echo "✅ SUCCESS! Certificates obtained successfully."
    echo ""
    echo "Next steps:"
    echo "  1. Start the main application:"
    echo "     ./start.sh"
    echo ""
else
    echo ""
    echo "❌ ERROR: Certificates were not created."
    echo "Please check the logs above for errors."
    exit 1
fi
