# Troubleshooting Guide

Comprehensive solutions for common issues with KNA History deployment.

## 🔍 Diagnostic Tools

### 🛠️ Quick Diagnostic Commands

```bash
# Overall system status
./status.sh

# Validate configuration
./validate-config.sh

# Check all containers
docker compose ps

# View logs
docker compose logs --tail=50

# Check disk space
df -h

# Check memory
free -h

# Test database connection
docker compose exec kna-historie python -c "
from kna_data.config import get_config
config = get_config()
engine = config.get_engine()
with engine.connect() as conn:
    print('✅ Database OK')
"
```

### 📊 System Health Check

```bash
#!/bin/bash
# diagnose.sh

echo "=== KNA History Diagnostic Report ==="
echo "Date: $(date)"
echo ""

echo "1. Docker Status:"
docker --version
docker compose version
echo ""

echo "2. Containers:"
docker compose ps
echo ""

echo "3. Disk Space:"
df -h | grep -E '(Filesystem|/data|/$)'
echo ""

echo "4. Memory:"
free -h
echo ""

echo "5. Recent Errors:"
docker compose logs --since="24h" | grep ERROR | tail -10
echo ""

echo "6. Configuration:"
./validate-config.sh
```

## 🚫 Application Issues

### ❌ Application Won't Start

**Symptoms:**
- Container exits immediately
- Health check fails
- Can't access website

**Diagnosis:**
```bash
# Check container status
docker compose ps kna-historie

# View logs
docker compose logs kna-historie

# Check configuration
./validate-config.sh
```

**Common Causes:**

#### Missing Environment Variables

**Check:**
```bash
# Verify .env file exists
ls -la .env

# Check required variables
grep -E '(SECRET_KEY|MARIADB_PASSWORD|DOMAIN_NAME)' .env
```

**Fix:**
```bash
# Copy template
cp env.example .env

# Edit with proper values
nano .env

# Restart
docker compose up -d
```

#### Configuration Syntax Error

**Check:**
```bash
# Validate docker-compose.yml
docker compose config

# Check for errors
docker compose config 2>&1 | grep -i error
```

**Fix:**
```bash
# Fix syntax errors in docker-compose.yml
# Common issues:
# - Incorrect indentation
# - Missing colons
# - Unquoted strings with special chars
```

#### Port Already in Use

**Check:**
```bash
# Check if ports 80/443 are in use
sudo lsof -i :80
sudo lsof -i :443
```

**Fix:**
```bash
# Stop conflicting service
sudo systemctl stop apache2  # or nginx, etc.

# Or change ports in docker-compose.yml
ports:
  - "8080:80"
  - "8443:443"
```

### ❌ Application Crashes

**Symptoms:**
- Container restarts frequently
- Random errors
- Intermittent availability

**Diagnosis:**
```bash
# Check restart count
docker compose ps

# View crash logs
docker compose logs --tail=200 kna-historie

# Check resource limits
docker stats kna-historie --no-stream
```

**Common Causes:**

#### Out of Memory

**Check:**
```bash
# Memory usage
docker stats kna-historie --no-stream

# System memory
free -h

# Check for OOM kills
dmesg | grep -i "out of memory"
```

**Fix:**
```bash
# Increase container memory limit
# Edit docker-compose.yml:
services:
  kna-historie:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase from 1G

# Restart
docker compose up -d
```

#### Database Connection Timeout

**Check:**
```bash
# Test database connection
docker compose exec kna-historie python -c "
import time
from kna_data.config import get_config
start = time.time()
config = get_config()
engine = config.get_engine()
with engine.connect() as conn:
    conn.execute('SELECT 1')
print(f'Connection time: {time.time() - start:.2f}s')
"
```

**Fix:**
```bash
# Increase connection timeout
# In config.py:
engine = create_engine(
    url,
    connect_args={'connect_timeout': 30}  # Increase from 10
)
```

## 🗄️ Database Issues

### ❌ Can't Connect to Database

**Symptoms:**
- "Database connection failed"
- Health check fails
- Application can't start

**Diagnosis:**
```bash
# Check MariaDB status
docker compose ps mariadb

# View MariaDB logs
docker compose logs mariadb

# Test connection
docker compose exec mariadb mysqladmin ping
```

**Common Causes:**

#### MariaDB Not Running

**Check:**
```bash
docker compose ps mariadb
```

**Fix:**
```bash
# Start MariaDB
docker compose up -d mariadb

# Check logs for errors
docker compose logs mariadb

# If persistent, restart
docker compose restart mariadb
```

#### Wrong Credentials

**Check:**
```bash
# Verify credentials in .env
cat .env | grep MARIADB

# Test connection
docker compose exec mariadb mysql -u root -p
```

**Fix:**
```bash
# Update .env with correct credentials
nano .env

# Restart application
docker compose restart kna-historie
```

#### Database Not Created

**Check:**
```bash
# List databases
docker compose exec mariadb mysql -u root -p -e "SHOW DATABASES;"
```

**Fix:**
```bash
# Create database
docker compose exec mariadb mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS kna;
CREATE DATABASE IF NOT EXISTS kna_users;
GRANT ALL PRIVILEGES ON kna.* TO 'kna'@'%';
GRANT ALL PRIVILEGES ON kna_users.* TO 'kna'@'%';
FLUSH PRIVILEGES;
"
```

### ❌ Database Corrupted

**Symptoms:**
- SQL errors in logs
- Missing data
- Inconsistent results

**Diagnosis:**
```bash
# Check tables
docker compose exec mariadb mysql -u root -p -e "
USE kna;
SHOW TABLES;
CHECK TABLE lid, uitvoering, rol, file;
"

# Check for errors
docker compose logs mariadb | grep ERROR
```

**Fix:**
```bash
# Repair tables
docker compose exec mariadb mysql -u root -p -e "
USE kna;
REPAIR TABLE lid;
REPAIR TABLE uitvoering;
REPAIR TABLE rol;
REPAIR TABLE file;
"

# If repair fails, restore from backup
gunzip < /data/backups/daily/latest.sql.gz | \
  docker compose exec -T mariadb mysql -u root -p kna
```

## 🌐 Network & SSL Issues

### ❌ Can't Access Website

**Symptoms:**
- "Connection refused"
- "This site can't be reached"
- Timeout errors

**Diagnosis:**
```bash
# Check if site is accessible
curl -I https://your-domain.com

# Check nginx status
docker compose ps nginx

# Check nginx logs
docker compose logs nginx

# Check DNS
dig your-domain.com
```

**Common Causes:**

#### Firewall Blocking

**Check:**
```bash
# Check firewall rules
sudo ufw status

# Check if ports open
sudo netstat -tlnp | grep -E '(80|443)'
```

**Fix:**
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Reload firewall
sudo ufw reload
```

#### Nginx Not Running

**Check:**
```bash
docker compose ps nginx
```

**Fix:**
```bash
# Restart nginx
docker compose restart nginx

# Check configuration
docker compose exec nginx nginx -t

# View errors
docker compose logs nginx
```

#### DNS Not Configured

**Check:**
```bash
# Check DNS resolution
dig your-domain.com

# Check IP matches server
curl ifconfig.me
```

**Fix:**
```bash
# Update DNS A record to point to server IP
# Wait for DNS propagation (up to 24 hours)

# Check DuckDNS (if using)
curl "https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip="
```

### ❌ SSL Certificate Issues

**Symptoms:**
- "Your connection is not private"
- "NET::ERR_CERT_DATE_INVALID"
- "SSL certificate problem"

**Diagnosis:**
```bash
# Check certificate
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -dates

# Check certificate files
ls -la /data/certbot/conf/live/your-domain.com/

# Check certbot logs
docker compose logs certbot-auto
```

**Common Causes:**

#### Certificate Expired

**Check:**
```bash
# Check expiry
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -enddate
```

**Fix:**
```bash
# Renew certificate
docker compose run --rm certbot renew

# Restart nginx
docker compose restart nginx

# Or use setup script
./setup-certificates.sh
```

#### Certificate Not Found

**Check:**
```bash
ls -la /data/certbot/conf/live/your-domain.com/
```

**Fix:**
```bash
# Obtain certificate
./setup-certificates.sh

# Or manually
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com
```

#### Wrong Domain in Certificate

**Check:**
```bash
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | \
  openssl x509 -noout -text | grep DNS
```

**Fix:**
```bash
# Remove old certificate
docker compose run --rm certbot delete

# Obtain new certificate with correct domain
./setup-certificates.sh
```

## 📁 File & Permission Issues

### ❌ Media Files Not Loading

**Symptoms:**
- Broken images
- 404 errors
- "File not found"

**Diagnosis:**
```bash
# Check if files exist
ls -la /data/kna_resources/

# Check permissions
stat /data/kna_resources/

# Check logs
docker compose logs kna-historie | grep "File not found"
```

**Common Causes:**

#### Wrong Permissions

**Check:**
```bash
ls -la /data/kna_resources/
# Should show: drwxr-xr-x 1000 1000
```

**Fix:**
```bash
# Fix permissions
sudo chown -R 1000:1000 /data/kna_resources
sudo chmod -R 755 /data/kna_resources

# Fix individual files
sudo find /data/kna_resources -type f -exec chmod 644 {} \;
sudo find /data/kna_resources -type d -exec chmod 755 {} \;
```

#### Files in Wrong Location

**Check:**
```bash
# Check folder structure
ls -la /data/kna_resources/
# Should match "folder" column in database
```

**Fix:**
```bash
# Move files to correct location
# Check database for expected folder names
docker compose exec mariadb mysql -u root -p -e "
USE kna;
SELECT DISTINCT folder FROM uitvoering;
"

# Ensure folders match
```

#### Missing Thumbnails

**Check:**
```bash
# Check for thumbnails
find /data/kna_resources -name "thumbnails" -type d
```

**Fix:**
```bash
# Regenerate thumbnails
# Admin → Maintenance → Regenerate Thumbnails

# Or via CLI
docker compose exec kna-historie python -m kna_data.cli thumbnails
```

### ❌ Can't Upload Files

**Symptoms:**
- Upload fails
- "Permission denied"
- "Disk quota exceeded"

**Diagnosis:**
```bash
# Check disk space
df -h /data

# Check upload directory permissions
ls -la /tmp/kna_uploads

# Check size limits
grep MAX_CONTENT_LENGTH .env
```

**Fix:**
```bash
# Free up disk space
docker system prune -a

# Create upload directory
mkdir -p /tmp/kna_uploads
chmod 777 /tmp/kna_uploads

# Increase upload limit (if needed)
# In docker-compose.yml:
environment:
  MAX_CONTENT_LENGTH: 100485760  # 100MB
```

## 🔧 Performance Issues

### ❌ Slow Response Times

**Symptoms:**
- Pages load slowly
- Timeouts
- High CPU usage

**Diagnosis:**
```bash
# Measure response time
time curl -s https://your-domain.com/ > /dev/null

# Check resource usage
docker stats --no-stream

# Check database performance
docker compose exec mariadb mysql -u root -p -e "SHOW PROCESSLIST;"
```

**Common Causes:**

#### Database Not Optimized

**Check:**
```bash
# Check table status
docker compose exec mariadb mysql -u root -p -e "
USE kna;
SHOW TABLE STATUS;
"
```

**Fix:**
```bash
# Optimize tables
docker compose exec mariadb mysql -u root -p -e "
USE kna;
OPTIMIZE TABLE lid, uitvoering, rol, file, file_leden;
"

# Update statistics
docker compose exec mariadb mysql -u root -p -e "
USE kna;
ANALYZE TABLE lid, uitvoering, rol, file, file_leden;
"
```

#### Too Many Requests

**Check:**
```bash
# Count recent requests
docker compose logs nginx | grep "$(date +%d/%b/%Y)" | wc -l
```

**Fix:**
```bash
# Add rate limiting in nginx
# Edit nginx.conf:
limit_req_zone $binary_remote_addr zone=limitzone:10m rate=10r/s;

location / {
    limit_req zone=limitzone burst=20;
    proxy_pass http://kna-historie:5000;
}
```

#### Insufficient Resources

**Check:**
```bash
# Check if containers are resource-constrained
docker stats
```

**Fix:**
```bash
# Increase resource limits
# Edit docker-compose.yml:
services:
  kna-historie:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## 🔄 Update Issues

### ❌ Update Fails

**Symptoms:**
- Update script errors
- Application won't start after update
- Data loss

**Diagnosis:**
```bash
# Check logs
cat /var/log/kna-updates.log

# Check current version
docker compose exec kna-historie python -c "from kna_data import __version__; print(__version__)"

# Check image
docker images | grep kna-history
```

**Fix:**
```bash
# Rollback to previous version
./update.sh rollback

# Or manually
docker compose down
echo "KNA_IMAGE_TAG=v1.0.0" >> .env
docker compose pull
docker compose up -d

# Restore database if needed
gunzip < /data/backups/auto-latest.sql.gz | \
  docker compose exec -T mariadb mysql -u root -p kna
```

## 💾 Backup/Restore Issues

### ❌ Backup Fails

**Symptoms:**
- No backup file created
- Backup file empty or corrupted
- Permission errors

**Diagnosis:**
```bash
# Check recent backups
ls -lht /data/backups/daily/ | head

# Check backup logs
cat /var/log/kna-backups.log

# Test backup manually
docker compose exec mariadb mysqldump -u root -p kna | head
```

**Fix:**
```bash
# Check disk space
df -h /data

# Check permissions
ls -la /data/backups

# Fix permissions
sudo chown -R root:root /data/backups
sudo chmod -R 755 /data/backups

# Test backup script
./backup.sh daily
```

### ❌ Restore Fails

**Symptoms:**
- SQL errors during restore
- Partial data restoration
- Application errors after restore

**Diagnosis:**
```bash
# Test backup file integrity
gunzip -t /data/backups/daily/kna_20260207.sql.gz

# Check file size
ls -lh /data/backups/daily/kna_20260207.sql.gz
```

**Fix:**
```bash
# Use different backup file
ls -lht /data/backups/daily/

# Restore with verbose output
gunzip < backup.sql.gz | docker compose exec -T mariadb mysql -u root -p kna -v

# Check for errors
docker compose logs mariadb | grep ERROR
```

## 🔐 Security Issues

### ❌ Can't Login

**Symptoms:**
- "Invalid credentials"
- Password not working
- Login page doesn't load

**Diagnosis:**
```bash
# Check users database
docker compose exec kna-historie python -c "
from kna_data.models import User, db
users = User.query.all()
for u in users:
    print(f'{u.username} - {u.role} - Active: {u.active}')
"

# Check admin password in .env
grep ADMIN_PASSWORD .env
```

**Fix:**
```bash
# Reset admin password
docker compose exec kna-historie python -c "
from kna_data.models import User, db
from werkzeug.security import generate_password_hash

admin = User.query.filter_by(username='admin').first()
admin.password_hash = generate_password_hash('NewPassword123!')
db.session.commit()
print('✅ Password reset')
"
```

### ❌ Session Issues

**Symptoms:**
- Logged out frequently
- "Session expired"
- Can't stay logged in

**Diagnosis:**
```bash
# Check SECRET_KEY
grep SECRET_KEY .env

# Check if SECRET_KEY changed recently
git log -p .env | grep SECRET_KEY
```

**Fix:**
```bash
# Don't change SECRET_KEY unnecessarily
# If you must change it, users will need to re-login

# Increase session timeout
# In config.py:
PERMANENT_SESSION_LIFETIME = timedelta(days=7)
```

## 📞 Getting Help

### 🆘 When to Seek Help

**Self-troubleshoot first if:**
- Issue is documented here
- Error message is clear
- Recent configuration change

**Seek help if:**
- Data loss or corruption
- Security breach suspected
- Undocumented error
- Multiple failed troubleshooting attempts

### 📋 Information to Provide

When asking for help, provide:

```bash
# System information
./diagnose.sh > diagnostic-report.txt

# Recent logs
docker compose logs --since="1h" > recent-logs.txt

# Configuration (remove secrets!)
cat .env | sed 's/\(PASSWORD\|SECRET\|TOKEN\)=.*/\1=REDACTED/' > config-sanitized.txt

# Error screenshots
# Screenshot of exact error message

# Steps to reproduce
# Detailed steps that led to the issue
```

### 🔗 Resources

- **Documentation:** https://docs.kna-history.org
- **GitHub Issues:** https://github.com/mark-me/kna-history/issues
- **Community Forum:** (if available)
- **Email Support:** admin@kna-hillegom.nl

## ✅ Prevention

### 🛡️ Best Practices

**To Avoid Issues:**

- [ ] Regular backups (daily minimum)
- [ ] Test backups monthly
- [ ] Monitor disk space
- [ ] Monitor resource usage
- [ ] Keep software updated
- [ ] Read release notes before updating
- [ ] Test updates in staging first
- [ ] Document configuration changes
- [ ] Regular security audits
- [ ] Keep logs for 30+ days

### 📚 Related Documentation

- [Configuration](configuration.md) - Proper configuration
- [Monitoring](monitoring.md) - Proactive monitoring
- [Backup](backup.md) - Backup best practices
- [Updates](updates.md) - Safe update procedures
- [Production](production.md) - Production setup
