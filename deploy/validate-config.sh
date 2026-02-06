#!/bin/bash
# validate-config.sh - Validate environment configuration before deployment

set -e

echo "=========================================="
echo "KNA History - Configuration Validator"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "âŒ ERROR: .env file not found!"
    echo ""
    echo "To fix:"
    echo "  cp env.example .env"
    echo "  nano .env"
    exit 1
fi

# Source environment variables
source .env

# Track issues
ERRORS=0
WARNINGS=0

echo "Checking required environment variables..."
echo ""

# Required variables
REQUIRED_VARS=(
    "FLASK_ENV:Environment selection (production/development/testing)"
    "SECRET_KEY:Flask secret key for session security"
    "MARIADB_HOST:MariaDB hostname"
    "MARIADB_USER:MariaDB username"
    "MARIADB_PASSWORD:MariaDB password"
    "MARIADB_ROOT_PASSWORD:MariaDB root password"
    "MARIADB_DATABASE:MariaDB database name"
    "DATABASE_URL:Flask-Login users database connection"
    "DIR_RESOURCES:Container resources directory path"
    "DIR_RESOURCES_HOST:Host resources directory path"
    "DIR_MARIADB:Host MariaDB data directory path"
    "ADMIN_PASSWORD:Default admin user password"
    "DOMAIN_NAME:Domain name for the application"
    "EMAIL_ADDRESS:Email for SSL certificates"
)

echo "1. Required Variables:"
for var_info in "${REQUIRED_VARS[@]}"; do
    IFS=':' read -r var desc <<< "$var_info"
    if [ -z "${!var}" ]; then
        echo "  âŒ $var - MISSING ($desc)"
        ((ERRORS++))
    else
        echo "  âœ… $var - Set"
    fi
done

echo ""
echo "2. Security Checks:"

# Check SECRET_KEY
if [ -n "$SECRET_KEY" ]; then
    if [[ "$SECRET_KEY" == *"change-this"* ]] || [[ "$SECRET_KEY" == *"your-secret"* ]] || [[ "$SECRET_KEY" == *"example"* ]]; then
        echo "  âŒ SECRET_KEY - Using default/example value (CRITICAL SECURITY ISSUE)"
        ((ERRORS++))
    elif [ ${#SECRET_KEY} -lt 32 ]; then
        echo "  âš  SECRET_KEY - Too short (recommended: 64+ characters)"
        ((WARNINGS++))
    else
        echo "  âœ… SECRET_KEY - Looks good (${#SECRET_KEY} characters)"
    fi
fi

# Check ADMIN_PASSWORD
if [ -n "$ADMIN_PASSWORD" ]; then
    if [[ "$ADMIN_PASSWORD" == "admin2026!" ]] || [[ "$ADMIN_PASSWORD" == *"change"* ]] || [[ "$ADMIN_PASSWORD" == "admin"* ]] && [ ${#ADMIN_PASSWORD} -lt 12 ]; then
        echo "  âŒ ADMIN_PASSWORD - Using weak/default password (SECURITY ISSUE)"
        ((ERRORS++))
    elif [ ${#ADMIN_PASSWORD} -lt 12 ]; then
        echo "  âš  ADMIN_PASSWORD - Too short (recommended: 16+ characters)"
        ((WARNINGS++))
    else
        echo "  âœ… ADMIN_PASSWORD - Looks good"
    fi
fi

# Check database passwords
if [ -n "$MARIADB_PASSWORD" ]; then
    if [ ${#MARIADB_PASSWORD} -lt 12 ]; then
        echo "  âš  MARIADB_PASSWORD - Too short (recommended: 16+ characters)"
        ((WARNINGS++))
    else
        echo "  âœ… MARIADB_PASSWORD - Looks good"
    fi
fi

if [ -n "$MARIADB_ROOT_PASSWORD" ]; then
    if [ ${#MARIADB_ROOT_PASSWORD} -lt 12 ]; then
        echo "  âš  MARIADB_ROOT_PASSWORD - Too short (recommended: 16+ characters)"
        ((WARNINGS++))
    else
        echo "  âœ… MARIADB_ROOT_PASSWORD - Looks good"
    fi
fi

echo ""
echo "3. Database Configuration:"

# Validate DATABASE_URL format
if [ -n "$DATABASE_URL" ]; then
    if [[ "$DATABASE_URL" =~ ^(mysql|postgresql|sqlite):// ]]; then
        echo "  âœ… DATABASE_URL - Valid format"
        
        # Check if it contains the MariaDB password (for consistency)
        if [[ "$DATABASE_URL" == *"mysql"* ]] && [[ "$DATABASE_URL" != *"$MARIADB_PASSWORD"* ]]; then
            echo "  âš  DATABASE_URL password differs from MARIADB_PASSWORD"
            ((WARNINGS++))
        fi
    else
        echo "  âŒ DATABASE_URL - Invalid format (should start with mysql://, postgresql://, or sqlite://)"
        ((ERRORS++))
    fi
fi

echo ""
echo "4. Directory Checks:"

# Check if directories exist
if [ -n "$DIR_RESOURCES_HOST" ]; then
    if [ -d "$DIR_RESOURCES_HOST" ]; then
        echo "  âœ… DIR_RESOURCES_HOST exists: $DIR_RESOURCES_HOST"
        # Check permissions
        if [ -w "$DIR_RESOURCES_HOST" ]; then
            echo "      âœ… Writable"
        else
            echo "      âš  Not writable (may need sudo chown -R 1000:1000)"
            ((WARNINGS++))
        fi
    else
        echo "  âš  DIR_RESOURCES_HOST does not exist: $DIR_RESOURCES_HOST"
        echo "      Will be created on first start"
        ((WARNINGS++))
    fi
fi

if [ -n "$DIR_MARIADB" ]; then
    if [ -d "$DIR_MARIADB" ]; then
        echo "  âœ… DIR_MARIADB exists: $DIR_MARIADB"
    else
        echo "  âš  DIR_MARIADB does not exist: $DIR_MARIADB"
        echo "      Will be created on first start"
        ((WARNINGS++))
    fi
fi

echo ""
echo "5. Docker Configuration:"

# Check if docker is running
if command -v docker &> /dev/null; then
    if docker info &>/dev/null; then
        echo "  âœ… Docker is running"
    else
        echo "  âŒ Docker is installed but not running"
        ((ERRORS++))
    fi
else
    echo "  âŒ Docker is not installed"
    ((ERRORS++))
fi

# Check if docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    echo "  âœ… docker-compose.yml found"
    
    # Validate docker-compose file
    if docker compose config &>/dev/null; then
        echo "  âœ… docker-compose.yml is valid"
    else
        echo "  âŒ docker-compose.yml has syntax errors"
        ((ERRORS++))
    fi
else
    echo "  âŒ docker-compose.yml not found"
    ((ERRORS++))
fi

echo ""
echo "6. SSL Certificate:"

if [ -n "$DOMAIN_NAME" ] && [ -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    echo "  âœ… SSL certificates found for $DOMAIN_NAME"
    
    # Check certificate expiry
    CERT_FILE="/data/certbot/conf/live/$DOMAIN_NAME/cert.pem"
    if [ -f "$CERT_FILE" ]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -gt 30 ]; then
            echo "      âœ… Valid for $DAYS_LEFT days"
        elif [ $DAYS_LEFT -gt 0 ]; then
            echo "      âš  Expires in $DAYS_LEFT days (consider renewal)"
            ((WARNINGS++))
        else
            echo "      âŒ Certificate expired!"
            ((ERRORS++))
        fi
    fi
else
    echo "  âš  SSL certificates not found"
    echo "      Run ./setup-certificates.sh to obtain certificates"
    ((WARNINGS++))
fi

echo ""
echo "========================================"
echo "Validation Summary"
echo "========================================"
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo "âŒ Configuration has ERRORS that must be fixed before deployment"
    echo ""
    echo "To generate secure secrets:"
    echo "  python3 -c \"import secrets; print(secrets.token_urlsafe(48))\""
    echo ""
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "âš  Configuration has warnings but can be deployed"
    echo "   Review the warnings above and address them if possible"
    echo ""
    exit 0
else
    echo "âœ… Configuration is valid and ready for deployment!"
    echo ""
    echo "Next steps:"
    if [ ! -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
        echo "  1. Set up SSL certificates:"
        echo "     ./setup-certificates.sh"
        echo "  2. Start the application:"
        echo "     ./start.sh"
    else
        echo "  1. Start the application:"
        echo "     ./start.sh"
    fi
    echo ""
    exit 0
fi
