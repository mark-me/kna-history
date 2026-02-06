#!/bin/bash
# status.sh - Check status of KNA History application and services

set -e

echo "=========================================="
echo "KNA History - System Status"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "âš  .env file not found - using defaults"
else
    source .env
fi

# Check Docker
echo "1. Docker Status:"
if command -v docker &> /dev/null; then
    if docker info &>/dev/null; then
        echo "  âœ… Docker is running"
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        echo "     Version: $DOCKER_VERSION"
    else
        echo "  âŒ Docker is not running"
    fi
else
    echo "  âŒ Docker is not installed"
fi

echo ""
echo "2. Container Status:"
if docker compose ps &>/dev/null; then
    docker compose ps
else
    echo "  No containers running (or docker-compose.yml not found)"
fi

echo ""
echo "3. Application Health:"

# Check if kna-historie is running
if docker ps --format '{{.Names}}' | grep -q "kna-historie"; then
    echo "  Container: âœ… Running"
    
    # Check health endpoint
    if curl -sf http://localhost:5000/health &>/dev/null; then
        HEALTH_STATUS=$(curl -s http://localhost:5000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "  Health:    âœ… $HEALTH_STATUS"
        
        # Get app version
        APP_VERSION=$(docker inspect kna-historie --format='{{index .Config.Env}}' | grep -o 'APP_VERSION=[^,]*' | cut -d'=' -f2 2>/dev/null || echo "unknown")
        echo "  Version:   $APP_VERSION"
    else
        echo "  Health:    âŒ Unhealthy (endpoint not responding)"
    fi
    
    # Get uptime
    UPTIME=$(docker inspect kna-historie --format='{{.State.StartedAt}}' | xargs -I {} date -d {} +%s)
    NOW=$(date +%s)
    UPTIME_SECONDS=$((NOW - UPTIME))
    UPTIME_HOURS=$((UPTIME_SECONDS / 3600))
    UPTIME_MINUTES=$(((UPTIME_SECONDS % 3600) / 60))
    echo "  Uptime:    ${UPTIME_HOURS}h ${UPTIME_MINUTES}m"
else
    echo "  Container: âŒ Not running"
    echo "  Health:    âŒ Not available"
fi

echo ""
echo "4. MariaDB Status:"

if docker ps --format '{{.Names}}' | grep -q "mariadb"; then
    echo "  Container: âœ… Running"
    
    # Check if database is responding
    if docker exec mariadb mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "  Database:  âœ… Responding"
        
        # Get database size
        if [ -n "$MARIADB_DATABASE" ]; then
            DB_SIZE=$(docker exec mariadb mysql -u root -p"$MARIADB_ROOT_PASSWORD" -e "
                SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)' 
                FROM information_schema.tables 
                WHERE table_schema = '$MARIADB_DATABASE';
            " --batch --skip-column-names 2>/dev/null || echo "unknown")
            echo "  Size:      ${DB_SIZE} MB"
        fi
    else
        echo "  Database:  âŒ Not responding"
    fi
else
    echo "  Container: âŒ Not running"
fi

echo ""
echo "5. Nginx Status:"

if docker ps --format '{{.Names}}' | grep -q "nginx"; then
    echo "  Container: âœ… Running"
    
    # Check if nginx is responding
    if curl -sf http://localhost &>/dev/null; then
        echo "  HTTP:      âœ… Responding"
    else
        echo "  HTTP:      âŒ Not responding"
    fi
    
    if curl -sfk https://localhost &>/dev/null; then
        echo "  HTTPS:     âœ… Responding"
    else
        echo "  HTTPS:     âš  Not responding (check SSL certificates)"
    fi
else
    echo "  Container: âŒ Not running"
fi

echo ""
echo "6. SSL Certificates:"

if [ -n "$DOMAIN_NAME" ] && [ -d "/data/certbot/conf/live/$DOMAIN_NAME" ]; then
    CERT_FILE="/data/certbot/conf/live/$DOMAIN_NAME/cert.pem"
    if [ -f "$CERT_FILE" ]; then
        EXPIRY=$(openssl x509 -enddate -noout -in "$CERT_FILE" | cut -d= -f2)
        EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s 2>/dev/null || echo 0)
        NOW_EPOCH=$(date +%s)
        DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
        
        if [ $DAYS_LEFT -gt 30 ]; then
            echo "  Status:    âœ… Valid for $DAYS_LEFT days"
        elif [ $DAYS_LEFT -gt 0 ]; then
            echo "  Status:    âš  Expires in $DAYS_LEFT days"
        else
            echo "  Status:    âŒ Expired!"
        fi
        echo "  Expiry:    $EXPIRY"
    fi
else
    echo "  Status:    âš  Not configured"
fi

echo ""
echo "7. Disk Usage:"

if [ -n "$DIR_RESOURCES_HOST" ] && [ -d "$DIR_RESOURCES_HOST" ]; then
    RESOURCES_SIZE=$(du -sh "$DIR_RESOURCES_HOST" 2>/dev/null | cut -f1)
    echo "  Resources: $RESOURCES_SIZE ($DIR_RESOURCES_HOST)"
fi

if [ -n "$DIR_MARIADB" ] && [ -d "$DIR_MARIADB" ]; then
    DB_DISK_SIZE=$(du -sh "$DIR_MARIADB" 2>/dev/null | cut -f1)
    echo "  Database:  $DB_DISK_SIZE ($DIR_MARIADB)"
fi

echo ""
echo "8. Resource Usage:"

if docker ps --format '{{.Names}}' | grep -q "kna-historie"; then
    APP_STATS=$(docker stats kna-historie --no-stream --format "{{.CPUPerc}} CPU, {{.MemUsage}} Memory" 2>/dev/null)
    echo "  App:       $APP_STATS"
fi

if docker ps --format '{{.Names}}' | grep -q "mariadb"; then
    DB_STATS=$(docker stats mariadb --no-stream --format "{{.CPUPerc}} CPU, {{.MemUsage}} Memory" 2>/dev/null)
    echo "  MariaDB:   $DB_STATS"
fi

echo ""
echo "9. Recent Errors (last 20 lines):"

if docker ps --format '{{.Names}}' | grep -q "kna-historie"; then
    ERROR_COUNT=$(docker logs kna-historie --tail 100 2>&1 | grep -i "error\|exception\|failed\|critical" | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "  âš  Found $ERROR_COUNT error-like messages in logs"
        docker logs kna-historie --tail 100 2>&1 | grep -i "error\|exception\|failed\|critical" | tail -5
    else
        echo "  âœ… No recent errors in application logs"
    fi
else
    echo "  âŒ Application not running"
fi

echo ""
echo "========================================"
echo "Quick Actions:"
echo "========================================"
echo "  View logs:           docker compose logs -f"
echo "  Restart app:         docker compose restart kna-historie"
echo "  Full restart:        docker compose restart"
echo "  Update app:          ./update.sh"
echo "  Check config:        ./validate-config.sh"
echo "  View detailed logs:  docker compose logs -f kna-historie"
echo ""
