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
    echo "Please copy env.example to .env and configure it first:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

# Source environment variables
source .env

# Validate required variables
if [ -z "$DOMAIN_NAME" ]; then
    echo "ERROR: DOMAIN_NAME not set in .env file"
    exit 1
fi

if [ -z "$EMAIL_ADDRESS" ]; then
    echo "ERROR: EMAIL_ADDRESS not set in .env file"
    exit 1
fi

echo "Domain: $DOMAIN_NAME"
echo "Email: $EMAIL_ADDRESS"
echo ""

# Check if certificates already exist
if [ -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo "âš  Certificates already exist at /data/certbot/conf/live/$DOMAIN_NAME"
    echo ""
    read -p "Renew certificates? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled. Existing certificates will be used."
        exit 0
    fi
    echo "Proceeding with renewal..."
fi

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

# Create certbot directories if they don't exist
echo "Creating certbot directories..."
sudo mkdir -p /data/certbot/conf
sudo mkdir -p /data/certbot/www

# Stop main services if running
echo "Stopping main services (if running)..."
docker compose down 2>/dev/null || true

# Stop anything else on port 80
echo "Checking for services on port 80..."
if sudo lsof -i :80 &>/dev/null; then
    echo "WARNING: Port 80 is in use"
    sudo lsof -i :80
    echo ""
    read -p "Try to stop the service? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(sudo lsof -ti :80)
        sudo kill $PID 2>/dev/null || true
        sleep 2
    fi
fi

# Run certbot initial
echo "Running certbot to obtain certificates..."
if [ -f "docker-compose.certbot-initial.yml" ]; then
    docker compose -f docker-compose.certbot-initial.yml up --build
else
    echo "WARNING: docker-compose.certbot-initial.yml not found"
    echo "Running certbot directly..."
    docker run -it --rm \
        -p 80:80 \
        -v /data/certbot/conf:/etc/letsencrypt \
        -v /data/certbot/www:/var/www/certbot \
        certbot/certbot certonly \
        --standalone \
        --preferred-challenges http \
        --email "$EMAIL_ADDRESS" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN_NAME"
fi

# Check if certificates were created
if [ -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo ""
    echo "âœ… SUCCESS! Certificates obtained successfully."
    echo ""
    echo "Certificate location: /data/certbot/conf/live/$DOMAIN_NAME"
    echo "Certificate files:"
    ls -lh "/data/certbot/conf/live/$DOMAIN_NAME/"
    echo ""
    echo "Next steps:"
    echo "  1. Verify certificate:"
    echo "     openssl x509 -in /data/certbot/conf/live/$DOMAIN_NAME/cert.pem -text -noout | grep -A2 Validity"
    echo ""
    echo "  2. Start the main application:"
    echo "     ./start.sh"
    echo ""
else
    echo ""
    echo "âŒ ERROR: Certificates were not created."
    echo ""
    echo "Common issues:"
    echo "  - Domain DNS not pointing to this server"
    echo "  - Port 80 blocked by firewall"
    echo "  - Domain validation failed"
    echo ""
    echo "Check the logs above for specific errors."
    echo ""
    echo "To debug:"
    echo "  1. Verify DNS: dig $DOMAIN_NAME"
    echo "  2. Check port 80: sudo lsof -i :80"
    echo "  3. Test connectivity: curl -I http://$DOMAIN_NAME"
    exit 1
fi
