# Monitoring & Health Checks

Comprehensive guide for monitoring the KNA History application in production.

## 🎯 Monitoring Strategy

### 📊 What to Monitor

**Application Health:**
- HTTP endpoint availability
- Response times
- Error rates
- User sessions

**Infrastructure:**
- Container status
- Resource usage (CPU, RAM)
- Disk space
- Network connectivity

**Database:**
- Connection pool
- Query performance
- Table sizes
- Replication status (if applicable)

**External Services:**
- SSL certificate expiry
- DNS resolution
- DuckDNS updates
- Email delivery

## 🏥 Health Checks

### 🔍 Application Health Endpoint

**Endpoint:** `GET /health`

**Purpose:** Quick application health verification

**Response (Healthy):**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

**Response (Unhealthy):**
```json
{
  "status": "unhealthy",
  "error": "Database connection failed: ...",
  "version": "1.0.0"
}
```

**HTTP Status Codes:**
- `200 OK` - Application healthy
- `503 Service Unavailable` - Application unhealthy

**Manual Check:**
```bash
# Basic check
curl https://your-domain.com/health

# With details
curl -s https://your-domain.com/health | jq .

# Check response time
time curl -s https://your-domain.com/health
```

### 📋 Status Script

**Using status.sh:**

```bash
# Run comprehensive status check
./status.sh
```

**Output Example:**
```
========================================
KNA History - System Status
========================================

1. Docker Status:
  ✅ Docker is running
     Version: 24.0.7

2. Container Status:
  NAME           STATUS         HEALTH    PORTS
  kna-historie   Up 2 days      healthy   5000/tcp
  mariadb        Up 2 days      healthy   3306/tcp
  nginx          Up 2 days      healthy   80/tcp,443/tcp
  certbot-auto   Up 2 days      -         
  duckdns        Up 2 days      -         

3. Application Health:
  URL:       https://kna-historie.duckdns.org
  Status:    ✅ healthy
  Database:  ✅ connected
  Version:   1.0.0
  Uptime:    2d 14h 23m

4. MariaDB Status:
  Container: ✅ Running
  Database:  ✅ Responding
  Size:      2.34 GB
  Tables:    7

5. Resource Usage:
  Container       CPU     Memory
  kna-historie    5.2%    512 MB / 2 GB
  mariadb         12.1%   896 MB / 2 GB
  nginx           0.1%    24 MB / 128 MB

6. Disk Usage:
  Path                    Used    Available    Usage%
  /                       15 GB   35 GB        30%
  /data/kna_resources     8.2 GB  N/A          N/A
  /data/mariadb           2.3 GB  N/A          N/A
  /data/backups           4.1 GB  N/A          N/A

7. SSL Certificate:
  Domain:    kna-historie.duckdns.org
  Valid:     ✅ Yes
  Expires:   2026-05-07 (90 days)
  Auto-renew: ✅ Enabled

8. Recent Errors:
  Last 24h: 0 errors
  Last 7d:  2 warnings

========================================
Overall Status: ✅ HEALTHY
========================================
```

## 📈 Resource Monitoring

### 💻 Container Resources

**Real-time Stats:**
```bash
# All containers
docker stats

# Specific container
docker stats kna-historie --no-stream

# Formatted output
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

**Historical Data:**
```bash
# Install monitoring tools
apt-get install sysstat

# Enable collection
systemctl enable sysstat
systemctl start sysstat

# View historical CPU usage
sar -u

# View historical memory
sar -r

# View historical disk I/O
sar -d
```

### 💾 Disk Monitoring

**Check Disk Usage:**
```bash
# Overall disk usage
df -h

# Specific directories
du -sh /data/*

# Find large files
find /data -type f -size +100M -ls

# Disk usage trends
df -h | grep /data >> /var/log/disk-usage.log
```

**Disk Space Alerts:**
```bash
#!/bin/bash
# disk-monitor.sh

THRESHOLD=80
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ $USAGE -gt $THRESHOLD ]; then
    echo "⚠️ Disk usage at ${USAGE}%!" | \
      mail -s "Disk Space Warning" admin@example.com
fi
```

**Add to Cron:**
```bash
# Check every hour
0 * * * * /opt/kna-history/disk-monitor.sh
```

### 🗄️ Database Monitoring

**Connection Pool:**
```bash
# Show connections
docker exec mariadb mysql -u root -p -e "SHOW PROCESSLIST;"

# Count connections
docker exec mariadb mysql -u root -p -e "
SELECT COUNT(*) as active_connections 
FROM information_schema.PROCESSLIST;
"

# Connection stats
docker exec mariadb mysql -u root -p -e "SHOW STATUS LIKE 'Threads%';"
```

**Table Sizes:**
```bash
# Database size
docker exec mariadb mysql -u root -p -e "
SELECT 
  table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'kna'
GROUP BY table_schema;
"

# Table sizes
docker exec mariadb mysql -u root -p -e "
SELECT 
  table_name AS 'Table',
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
  table_rows AS 'Rows'
FROM information_schema.TABLES
WHERE table_schema = 'kna'
ORDER BY (data_length + index_length) DESC;
"
```

**Query Performance:**
```bash
# Slow queries
docker exec mariadb mysql -u root -p -e "
SELECT * FROM mysql.slow_log 
ORDER BY start_time DESC 
LIMIT 10;
"

# Query cache stats
docker exec mariadb mysql -u root -p -e "
SHOW STATUS LIKE 'Qcache%';
"
```

## 🔔 Alerting

### 📧 Email Alerts

**Setup Email Notifications:**

```bash
# Install mailutils
apt-get install mailutils

# Configure SMTP (optional)
# Edit /etc/postfix/main.cf

# Test email
echo "Test alert from KNA History" | \
  mail -s "Test Alert" admin@example.com
```

**Alert Script:**
```bash
#!/bin/bash
# alert.sh

SEVERITY=$1  # critical, warning, info
SUBJECT=$2
MESSAGE=$3
EMAIL="admin@example.com"

# Format message
FORMATTED="[${SEVERITY^^}] ${MESSAGE}

Time: $(date)
Host: $(hostname)
"

# Send email
echo "$FORMATTED" | mail -s "KNA History: ${SUBJECT}" $EMAIL

# Log alert
echo "$(date) [$SEVERITY] $SUBJECT: $MESSAGE" >> /var/log/kna-alerts.log
```

**Usage:**
```bash
./alert.sh critical "Database Down" "MariaDB container not responding"
./alert.sh warning "High CPU" "CPU usage at 85%"
./alert.sh info "Backup Complete" "Daily backup successful"
```

### 🚨 Automated Monitoring

**Health Check Monitor:**
```bash
#!/bin/bash
# health-monitor.sh

URL="https://your-domain.com/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ "$RESPONSE" != "200" ]; then
    ./alert.sh critical "Health Check Failed" \
      "HTTP $RESPONSE from $URL"
    exit 1
fi

# Check response content
CONTENT=$(curl -s $URL | jq -r '.status')
if [ "$CONTENT" != "healthy" ]; then
    ./alert.sh critical "Application Unhealthy" \
      "Status: $CONTENT"
    exit 1
fi

echo "✅ Health check passed"
```

**Resource Monitor:**
```bash
#!/bin/bash
# resource-monitor.sh

# CPU threshold
CPU_THRESHOLD=80
CPU_USAGE=$(docker stats kna-historie --no-stream --format "{{.CPUPerc}}" | sed 's/%//')

if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    ./alert.sh warning "High CPU Usage" "CPU at ${CPU_USAGE}%"
fi

# Memory threshold
MEM_THRESHOLD=80
MEM_USAGE=$(docker stats kna-historie --no-stream --format "{{.MemPerc}}" | sed 's/%//')

if (( $(echo "$MEM_USAGE > $MEM_THRESHOLD" | bc -l) )); then
    ./alert.sh warning "High Memory Usage" "Memory at ${MEM_USAGE}%"
fi
```

**Add to Cron:**
```bash
# Health check every 5 minutes
*/5 * * * * /opt/kna-history/health-monitor.sh

# Resource check every 15 minutes
*/15 * * * * /opt/kna-history/resource-monitor.sh
```

## 📊 External Monitoring

### 🌐 Uptime Monitoring Services

**UptimeRobot (Free):**

1. Sign up at https://uptimerobot.com
2. Add new monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: KNA History
   - URL: `https://your-domain.com/health`
   - Monitoring Interval: 5 minutes
3. Add alert contacts (email, SMS)
4. Configure notifications

**Pingdom:**

1. Sign up at https://www.pingdom.com
2. Add uptime check:
   - Name: KNA History
   - URL: `https://your-domain.com/health`
   - Check interval: 1 minute
   - Alert when: Down
3. Add integrations (email, Slack, PagerDuty)

**Better Uptime:**

1. Sign up at https://betteruptime.com
2. Create monitor:
   - Type: HTTP
   - URL: `https://your-domain.com/health`
   - Interval: 30 seconds
   - Expected status: 200
   - Expected response: `"status":"healthy"`
3. Configure on-call rotations

### 📱 Status Page

**Create Public Status Page:**

Using Better Uptime:
1. Enable status page
2. Customize branding
3. Share URL: `https://status.kna-history.org`

Custom status page:
```html
<!-- status.html -->
<!DOCTYPE html>
<html>
<head>
    <title>KNA History Status</title>
    <meta http-equiv="refresh" content="60">
</head>
<body>
    <h1>KNA History System Status</h1>
    <div id="status"></div>
    
    <script>
        fetch('https://your-domain.com/health')
            .then(r => r.json())
            .then(data => {
                document.getElementById('status').innerHTML = 
                    data.status === 'healthy' ? 
                    '🟢 All systems operational' :
                    '🔴 System issues detected';
            })
            .catch(() => {
                document.getElementById('status').innerHTML = 
                    '🔴 System unavailable';
            });
    </script>
</body>
</html>
```

## 📊 Logging

### 📝 Application Logs

**View Logs:**
```bash
# All containers
docker compose logs

# Specific container
docker compose logs kna-historie

# Follow mode (real-time)
docker compose logs -f kna-historie

# Last N lines
docker compose logs --tail=100 kna-historie

# Since timestamp
docker compose logs --since="2026-02-07T10:00:00" kna-historie

# Multiple containers
docker compose logs kna-historie mariadb
```

**Search Logs:**
```bash
# Grep for errors
docker compose logs kna-historie | grep ERROR

# Grep for specific user
docker compose logs kna-historie | grep "user@example.com"

# Count errors
docker compose logs kna-historie | grep ERROR | wc -l

# Errors in last hour
docker compose logs --since="1h" kna-historie | grep ERROR
```

### 🗂️ Log Rotation

**Configure Docker Logging:**

In `docker-compose.yml`:
```yaml
services:
  kna-historie:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service,environment"
```

**System Log Rotation:**

```bash
# Create logrotate config
cat > /etc/logrotate.d/kna-history << 'EOF'
/var/log/kna-history/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker compose -f /opt/kna-history/docker-compose.yml restart kna-historie > /dev/null
    endscript
}
EOF
```

### 🔍 Log Analysis

**Error Summary:**
```bash
#!/bin/bash
# log-summary.sh

echo "=== KNA History Log Summary ==="
echo "Date: $(date)"
echo ""

# Error count by type
echo "Errors (last 24h):"
docker compose logs --since="24h" kna-historie | \
  grep ERROR | \
  cut -d: -f4- | \
  sort | uniq -c | sort -rn

# Most active users
echo ""
echo "Most active users (last 7d):"
docker compose logs --since="7d" kna-historie | \
  grep "login" | \
  grep -oP 'user=\K[^ ]+' | \
  sort | uniq -c | sort -rn | head -10

# Request count by endpoint
echo ""
echo "Top endpoints (last 24h):"
docker compose logs --since="24h" nginx | \
  grep -oP 'GET \K[^ ]+' | \
  cut -d? -f1 | \
  sort | uniq -c | sort -rn | head -10
```

**Run Daily:**
```bash
# Add to cron
0 8 * * * /opt/kna-history/log-summary.sh | mail -s "Daily Log Summary" admin@example.com
```

## 🔐 SSL Certificate Monitoring

### 📅 Certificate Expiry

**Check Expiry Date:**
```bash
# Via OpenSSL
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Extract expiry only
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -enddate

# Days until expiry
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -checkend 0

# Days remaining
EXPIRY=$(echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x_509 -noout -enddate | cut -d= -f2)
DAYS=$(( ($(date -d "$EXPIRY" +%s) - $(date +%s)) / 86400 ))
echo "Certificate expires in $DAYS days"
```

**Certificate Monitor Script:**
```bash
#!/bin/bash
# cert-monitor.sh

DOMAIN="your-domain.com"
WARN_DAYS=30

# Get expiry date
EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | \
  openssl x509 -noout -enddate | cut -d= -f2)

# Calculate days remaining
DAYS=$(( ($(date -d "$EXPIRY" +%s) - $(date +%s)) / 86400 ))

echo "SSL certificate for $DOMAIN expires in $DAYS days"

# Alert if expiring soon
if [ $DAYS -lt $WARN_DAYS ]; then
    ./alert.sh warning "SSL Certificate Expiring" \
      "Certificate expires in $DAYS days"
fi

if [ $DAYS -lt 0 ]; then
    ./alert.sh critical "SSL Certificate EXPIRED" \
      "Certificate expired ${DAYS#-} days ago!"
fi
```

**Add to Cron:**
```bash
# Check daily at 9 AM
0 9 * * * /opt/kna-history/cert-monitor.sh
```

## 📈 Performance Metrics

### ⚡ Response Time Monitoring

**Measure Response Times:**
```bash
# Simple timing
time curl -s https://your-domain.com/ > /dev/null

# Detailed timing
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/

# curl-format.txt:
     time_namelookup:  %{time_namelookup}s\n
        time_connect:  %{time_connect}s\n
     time_appconnect:  %{time_appconnect}s\n
    time_pretransfer:  %{time_pretransfer}s\n
       time_redirect:  %{time_redirect}s\n
  time_starttransfer:  %{time_starttransfer}s\n
                     ----------\n
          time_total:  %{time_total}s\n
```

**Continuous Monitoring:**
```bash
#!/bin/bash
# response-time-monitor.sh

URL="https://your-domain.com/"
LOG="/var/log/kna-response-times.log"

while true; do
    TIME=$(curl -w "%{time_total}" -o /dev/null -s $URL)
    echo "$(date +%s),$TIME" >> $LOG
    
    # Alert if slow
    if (( $(echo "$TIME > 2" | bc -l) )); then
        ./alert.sh warning "Slow Response" "Response time: ${TIME}s"
    fi
    
    sleep 60
done
```

### 📊 Metrics Collection

**Using Prometheus (Advanced):**

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
```

## 🆘 Troubleshooting Monitoring

### ❌ Health Check Fails

**Symptoms:** Health endpoint returns 503

**Debug:**
```bash
# Check logs
docker compose logs kna-historie

# Check database
docker compose exec mariadb mysqladmin ping

# Test connection manually
docker compose exec kna-historie python -c "
from kna_data.config import get_config
config = get_config()
engine = config.get_engine()
with engine.connect() as conn:
    conn.execute('SELECT 1')
"
```

### ❌ No Metrics/Logs

**Symptoms:** Monitoring shows no data

**Check:**
```bash
# Container running?
docker compose ps

# Logs accessible?
docker compose logs --tail=10

# Disk space?
df -h

# Permissions?
ls -la /var/log/kna-history/
```

## 📚 Related Documentation

- [Configuration](configuration.md) - Monitoring configuration
- [Troubleshooting](troubleshooting.md) - Debugging issues
- [Backup](backup.md) - Backup monitoring
- [Updates](updates.md) - Update monitoring
- [Production](production.md) - Production monitoring setup
