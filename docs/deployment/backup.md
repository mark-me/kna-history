# Backup & Restore Guide

Comprehensive guide for backing up and restoring KNA History data.

## 💾 Backup Strategy

### 🎯 What to Backup

**Critical Data:**
1. **MariaDB Database** - All historical data
2. **Users Database** - Authentication data
3. **Configuration Files** - `.env`, `docker-compose.yml`
4. **Media Files** - Photos, videos, documents

**Optional:**
- Application logs
- Nginx configuration
- SSL certificates (auto-renewable)

### 📅 Backup Schedule

**Recommended Schedule:**

| Frequency | Type | Retention | What | Priority |
|-----------|------|-----------|------|----------|
| **Hourly** | Incremental | 24 hours | Database only | High traffic |
| **Daily** | Full | 30 days | Database + config | Standard |
| **Weekly** | Full | 90 days | Everything | Standard |
| **Monthly** | Full | 1 year | Everything | Archive |
| **Yearly** | Full | Permanent | Everything | Archive |

**Before:**
- Every update/upgrade
- Major configuration changes
- Before database maintenance
- Before testing risky operations

## 🔄 Automated Backups

### 🤖 Using Backup Script

The `backup.sh` script handles automated backups.

**Daily Backup:**
```bash
# Run backup
./backup.sh daily

# What it does:
# 1. Dumps MariaDB database
# 2. Compresses (gzip)
# 3. Saves to /data/backups/daily/
# 4. Rotates old backups (keeps 30 days)
# 5. Logs to /var/log/kna-backups.log
```

**Weekly Backup:**
```bash
./backup.sh weekly

# Includes:
# - Database dump
# - Configuration files
# - Saves to /data/backups/weekly/
# - Keeps 12 weeks
```

**Full Backup:**
```bash
./backup.sh full

# Includes everything:
# - Database
# - Configuration
# - Media files (optional, can be huge)
# - Saves to /data/backups/monthly/
```

### ⏰ Cron Scheduling

**Setup Automated Backups:**

```bash
# Edit crontab
crontab -e

# Add backup jobs:

# Daily backup at 2 AM
0 2 * * * /opt/kna-history/backup.sh daily >> /var/log/kna-backups.log 2>&1

# Weekly backup on Sunday at 3 AM
0 3 * * 0 /opt/kna-history/backup.sh weekly >> /var/log/kna-backups.log 2>&1

# Monthly backup on 1st at 4 AM
0 4 1 * * /opt/kna-history/backup.sh full >> /var/log/kna-backups.log 2>&1

# Verify cron jobs
crontab -l
```

### 📧 Backup Notifications

**Email on Completion:**

```bash
# Configure in backup.sh
EMAIL="admin@example.com"

# Or use cron with mail
0 2 * * * /opt/kna-history/backup.sh daily | mail -s "KNA Backup: $(date)" admin@example.com
```

## 💽 Manual Backups

### 🗄️ Database Backup

**MariaDB (KNA Data):**

```bash
# Simple dump
docker exec mariadb mysqldump \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  kna > kna_backup_$(date +%Y%m%d_%H%M%S).sql

# Compressed dump
docker exec mariadb mysqldump \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  kna | gzip > kna_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# With routines and triggers
docker exec mariadb mysqldump \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  --routines \
  --triggers \
  kna | gzip > kna_full_backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

**Users Database:**

```bash
# If using MariaDB for users
docker exec mariadb mysqldump \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  kna_users | gzip > users_backup_$(date +%Y%m%d_%H%M%S).sql.gz

# If using SQLite for users (dev)
cp dev.db dev_backup_$(date +%Y%m%d_%H%M%S).db
```

**All Databases:**

```bash
# Backup all databases at once
docker exec mariadb mysqldump \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  --all-databases | gzip > all_databases_$(date +%Y%m%d_%H%M%S).sql.gz
```

### 📁 Configuration Backup

```bash
# Backup configuration files
tar -czf config_backup_$(date +%Y%m%d).tar.gz \
  /opt/kna-history/.env \
  /opt/kna-history/docker-compose.yml \
  /opt/kna-history/*.sh

# Or copy to safe location
cp /opt/kna-history/.env /data/backups/config/.env.$(date +%Y%m%d)
```

### 🖼️ Media Files Backup

**Small Archives:**
```bash
# Tar and compress
tar -czf media_backup_$(date +%Y%m%d).tar.gz /data/kna_resources/

# Check size
ls -lh media_backup_*.tar.gz
```

**Large Archives:**
```bash
# Use rsync for incremental backups
rsync -av --progress \
  /data/kna_resources/ \
  /data/backups/media/

# Or split into chunks
tar -czf - /data/kna_resources/ | split -b 1G - media_backup_$(date +%Y%m%d).tar.gz.part
```

**Selective Backup:**
```bash
# Only recent media (last 90 days)
find /data/kna_resources -type f -mtime -90 | \
  tar -czf recent_media_$(date +%Y%m%d).tar.gz -T -

# Only specific performance
tar -czf annie_backup.tar.gz /data/kna_resources/annie_2015/
```

## 📤 Backup Storage

### 💾 Local Storage

**Backup Directory Structure:**
```
/data/backups/
├── daily/
│   ├── kna_20260207_020000.sql.gz
│   ├── kna_20260206_020000.sql.gz
│   └── ...
├── weekly/
│   ├── kna_20260207_030000.tar.gz
│   └── ...
├── monthly/
│   ├── kna_202602_full.tar.gz
│   └── ...
└── manual/
    └── kna_before_update_v2.sql.gz
```

**Disk Space Management:**
```bash
# Check backup disk usage
du -sh /data/backups/*

# Remove old backups (daily older than 30 days)
find /data/backups/daily -name "*.sql.gz" -mtime +30 -delete

# Remove old backups (weekly older than 90 days)
find /data/backups/weekly -name "*.tar.gz" -mtime +90 -delete
```

### ☁️ Off-Site Backup

**Rsync to Remote Server:**
```bash
# Setup SSH key-based auth first
ssh-copy-id backup@backup-server.com

# Rsync backups
rsync -avz --progress \
  /data/backups/ \
  backup@backup-server.com:/backups/kna-history/

# Add to cron (daily at 5 AM)
0 5 * * * rsync -az /data/backups/ backup@backup-server:/backups/kna-history/
```

**AWS S3:**
```bash
# Install AWS CLI
apt-get install awscli

# Configure
aws configure

# Upload to S3
aws s3 sync /data/backups/ s3://my-bucket/kna-history-backups/

# Add to cron
0 6 * * * aws s3 sync /data/backups/ s3://my-bucket/kna-history-backups/
```

**Backblaze B2:**
```bash
# Install B2 CLI
pip install b2

# Authorize
b2 authorize-account <keyID> <applicationKey>

# Upload
b2 sync /data/backups/ b2://my-bucket/kna-history/

# Add to cron
0 7 * * * b2 sync /data/backups/ b2://my-bucket/kna-history/
```

### 🔐 Encrypted Backups

**Encrypt with GPG:**
```bash
# Generate key (first time only)
gpg --full-generate-key

# Encrypt backup
gpg --encrypt --recipient admin@example.com \
  kna_backup_20260207.sql.gz

# Creates: kna_backup_20260207.sql.gz.gpg

# Decrypt
gpg --decrypt kna_backup_20260207.sql.gz.gpg > kna_backup_20260207.sql.gz
```

**Encrypt with OpenSSL:**
```bash
# Encrypt
openssl enc -aes-256-cbc -salt \
  -in kna_backup.sql.gz \
  -out kna_backup.sql.gz.enc \
  -k YourStrongPassword

# Decrypt
openssl enc -aes-256-cbc -d \
  -in kna_backup.sql.gz.enc \
  -out kna_backup.sql.gz \
  -k YourStrongPassword
```

## ♻️ Restore Procedures

### 🔄 Database Restore

**Full Database Restore:**

```bash
# 1. Stop application
docker compose down kna-historie

# 2. Decompress backup
gunzip kna_backup_20260207.sql.gz

# 3. Restore to MariaDB
docker exec -i mariadb mysql \
  -u root \
  -p${MARIADB_ROOT_PASSWORD} \
  kna < kna_backup_20260207.sql

# 4. Restart application
docker compose up -d kna-historie

# 5. Verify
curl https://your-domain.com/health
```

**Restore from Compressed Backup:**
```bash
# Direct restore from compressed backup
gunzip < kna_backup_20260207.sql.gz | \
  docker exec -i mariadb mysql -u root -p${MARIADB_ROOT_PASSWORD} kna
```

**Restore Specific Table:**
```bash
# Extract specific table from dump
sed -n '/CREATE TABLE `lid`/,/CREATE TABLE/p' kna_backup.sql > lid_only.sql

# Restore only that table
docker exec -i mariadb mysql -u root -p${MARIADB_ROOT_PASSWORD} kna < lid_only.sql
```

### 📁 Configuration Restore

```bash
# Restore .env file
cp /data/backups/config/.env.20260206 /opt/kna-history/.env

# Restore all config files
tar -xzf config_backup_20260206.tar.gz -C /

# Verify permissions
chmod 600 /opt/kna-history/.env
```

### 🖼️ Media Files Restore

**Full Restore:**
```bash
# Stop application
docker compose down kna-historie

# Restore from tar
tar -xzf media_backup_20260206.tar.gz -C /

# Or from rsync backup
rsync -av /data/backups/media/ /data/kna_resources/

# Fix permissions
chown -R 1000:1000 /data/kna_resources

# Restart application
docker compose up -d kna-historie

# Regenerate thumbnails
# Admin → Maintenance → Regenerate Thumbnails
```

**Restore Single Performance:**
```bash
# Extract specific folder
tar -xzf media_backup_20260206.tar.gz \
  --strip-components=3 \
  data/kna_resources/annie_2015

# Move to correct location
mv annie_2015 /data/kna_resources/

# Fix permissions
chown -R 1000:1000 /data/kna_resources/annie_2015
```

## 🚨 Disaster Recovery

### 💥 Complete System Recovery

**Scenario:** Server completely lost

**Recovery Steps:**

1. **Provision New Server**
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com | sh
   ```

2. **Restore Application Files**
   ```bash
   # Clone repository or download release
   git clone https://github.com/mark-me/kna-history.git /opt/kna-history
   cd /opt/kna-history
   ```

3. **Restore Configuration**
   ```bash
   # Copy .env from backup
   cp /path/to/backup/.env .
   ```

4. **Restore Database**
   ```bash
   # Create directories
   mkdir -p /data/{kna_resources,mariadb,certbot,backups}
   
   # Start MariaDB only
   docker compose up -d mariadb
   
   # Wait for MariaDB to be ready
   sleep 30
   
   # Restore database
   gunzip < latest_backup.sql.gz | \
     docker exec -i mariadb mysql -u root -p kna
   ```

5. **Restore Media Files**
   ```bash
   # Restore from backup
   tar -xzf media_backup_latest.tar.gz -C /
   chown -R 1000:1000 /data/kna_resources
   ```

6. **Start Application**
   ```bash
   # Obtain new SSL certificates
   ./setup-certificates.sh
   
   # Start all services
   docker compose up -d
   
   # Verify
   ./status.sh
   ```

7. **Verify Data Integrity**
   ```bash
   # Check database
   docker exec mariadb mysql -u root -p -e "
   USE kna;
   SELECT COUNT(*) FROM lid;
   SELECT COUNT(*) FROM uitvoering;
   SELECT COUNT(*) FROM file;
   "
   
   # Test application
   curl https://your-domain.com/health
   
   # Test admin login
   # Test viewing performances
   # Test media display
   ```

### 🔧 Partial Recovery

**Scenario:** Database corrupted, but media files intact

```bash
# 1. Stop application
docker compose down kna-historie

# 2. Backup current database (even if corrupted)
docker exec mariadb mysqldump -u root -p kna > corrupted_$(date +%Y%m%d).sql

# 3. Restore from latest good backup
gunzip < /data/backups/daily/kna_20260206.sql.gz | \
  docker exec -i mariadb mysql -u root -p kna

# 4. Restart and verify
docker compose up -d kna-historie
```

**Scenario:** Media files lost, but database intact

```bash
# 1. Restore media from backup
tar -xzf /data/backups/weekly/kna_media_20260206.tar.gz -C /

# 2. Fix permissions
chown -R 1000:1000 /data/kna_resources

# 3. Regenerate thumbnails
# Admin → Maintenance → Regenerate Thumbnails

# 4. Verify media display
```

## ✅ Backup Verification

### 🔍 Testing Backups

**Monthly Backup Test:**

```bash
#!/bin/bash
# test-backup.sh

BACKUP_FILE="/data/backups/daily/kna_$(date +%Y%m%d)*.sql.gz"

echo "Testing backup: $BACKUP_FILE"

# 1. Check file exists and is not empty
if [ ! -s "$BACKUP_FILE" ]; then
    echo "❌ Backup file missing or empty!"
    exit 1
fi

# 2. Test decompression
if ! gunzip -t "$BACKUP_FILE"; then
    echo "❌ Backup file corrupted!"
    exit 1
fi

# 3. Test SQL syntax (first 100 lines)
if ! gunzip < "$BACKUP_FILE" | head -100 | mysql --execute=""; then
    echo "❌ Backup SQL syntax invalid!"
    exit 1
fi

echo "✅ Backup file is valid"

# 4. Test restore in temporary database (optional)
# This is more thorough but takes time and resources
```

**Automated Verification:**
```bash
# Add to cron (daily at 8 AM)
0 8 * * * /opt/kna-history/test-backup.sh >> /var/log/backup-tests.log 2>&1
```

### 📊 Backup Integrity

**Check Backup Sizes:**
```bash
# Compare backup sizes (should be similar)
ls -lh /data/backups/daily/ | tail -7

# Alert if backup is too small
LATEST_SIZE=$(stat -f%z "/data/backups/daily/kna_$(date +%Y%m%d)*.sql.gz")
if [ $LATEST_SIZE -lt 1000000 ]; then  # Less than 1MB
    echo "⚠️ Backup size suspiciously small!"
fi
```

**Verify Backup Contents:**
```bash
# List tables in backup
gunzip < kna_backup.sql.gz | grep "CREATE TABLE"

# Count records per table
gunzip < kna_backup.sql.gz | grep "INSERT INTO" | cut -d'`' -f2 | sort | uniq -c
```

## 📋 Backup Checklist

### ✅ Daily

- [ ] Automated database backup ran successfully
- [ ] Backup file created and not empty
- [ ] Backup compressed properly
- [ ] Old backups rotated (>30 days removed)
- [ ] No errors in backup log

### ✅ Weekly

- [ ] Full backup completed
- [ ] Configuration files backed up
- [ ] Backup copied to off-site storage
- [ ] Backup integrity verified
- [ ] Backup restoration tested

### ✅ Monthly

- [ ] Complete full backup (including media)
- [ ] Disaster recovery plan reviewed
- [ ] Backup retention policy enforced
- [ ] Off-site backups verified
- [ ] Recovery procedures tested
- [ ] Backup documentation updated

### ✅ Before Major Changes

- [ ] Manual backup created
- [ ] Backup labeled with change description
- [ ] Backup verified before proceeding
- [ ] Rollback plan documented
- [ ] Team notified of backup location

## 📊 Monitoring Backups

### 🔔 Backup Alerts

**Monitor Backup Success:**

```bash
#!/bin/bash
# backup-monitor.sh

# Check if today's backup exists
TODAY=$(date +%Y%m%d)
BACKUP="/data/backups/daily/kna_${TODAY}*.sql.gz"

if [ ! -f $BACKUP ]; then
    echo "❌ Today's backup missing!" | \
      mail -s "KNA Backup FAILED" admin@example.com
    exit 1
fi

# Check backup age (should be less than 24 hours)
AGE=$(find $BACKUP -mtime +1)
if [ ! -z "$AGE" ]; then
    echo "⚠️ Backup older than 24 hours!" | \
      mail -s "KNA Backup WARNING" admin@example.com
fi
```

**Add to Cron:**
```bash
# Check at 9 AM daily
0 9 * * * /opt/kna-history/backup-monitor.sh
```

### 📈 Backup Metrics

**Track Backup Growth:**
```bash
# Log backup sizes
echo "$(date +%Y-%m-%d),$(du -sh /data/backups/ | cut -f1)" >> \
  /var/log/backup-sizes.log

# Plot growth over time
gnuplot -e "set datafile separator ','; plot '/var/log/backup-sizes.log' using 1:2 with lines"
```

## 🆘 Backup Troubleshooting

### ❌ Backup Fails

**Symptoms:** Backup script returns error

**Check:**
```bash
# Disk space
df -h /data

# Database running
docker compose ps mariadb

# Permissions
ls -la /data/backups

# Manual backup test
docker exec mariadb mysqldump -u root -p kna | head
```

### ❌ Restore Fails

**Symptoms:** Error during restore

**Solutions:**
```bash
# Check backup file integrity
gunzip -t kna_backup.sql.gz

# Check database is running
docker compose ps mariadb

# Try table-by-table restore
# Split large dump into smaller files
```

### ❌ Backup Too Large

**Symptoms:** Backups consuming too much space

**Solutions:**
```bash
# Compress better
gzip -9 kna_backup.sql  # Maximum compression

# Exclude large tables (if not needed)
mysqldump --ignore-table=kna.large_table ...

# Incremental backups
# Only backup changed data
```

## 📚 Related Documentation

- [Configuration](configuration.md) - Configuration backup
- [Updates](updates.md) - Pre-update backups
- [Monitoring](monitoring.md) - Backup monitoring
- [Troubleshooting](troubleshooting.md) - Recovery issues
- [Production](production.md) - Production backup setup
