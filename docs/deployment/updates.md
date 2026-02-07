# Updates Guide

Guide for updating the KNA History application safely and efficiently.

## 🔄 Update Strategy

### 📅 Update Schedule

**Recommended:**
- **Security updates:** Immediately when available
- **Minor updates:** Monthly
- **Major updates:** Quarterly (after testing)

**Release Channels:**
- `latest` - Latest stable release
- `vX.Y.Z` - Specific version tags
- `develop` - Development branch (not for production)

### 📊 Update Types

**Security Updates** 🔒
- Critical security patches
- Apply immediately
- Minimal testing needed

**Minor Updates** 🔧
- Bug fixes
- Performance improvements
- New features (non-breaking)
- Test before deploying

**Major Updates** 🚀
- Breaking changes
- Database migrations
- Extensive testing required
- Plan maintenance window

## 🎯 Pre-Update Checklist

### ✅ Before Every Update

- [ ] Read release notes
- [ ] Check breaking changes
- [ ] Backup database and media
- [ ] Test in staging (if available)
- [ ] Plan rollback procedure
- [ ] Schedule maintenance window
- [ ] Notify users (if needed)
- [ ] Verify disk space

### 📋 Release Notes Review

Check for:
- Database schema changes
- Configuration changes
- Deprecated features
- New dependencies
- Performance impacts

## 🚀 Update Methods

### 🎬 Method 1: Automated Update Script

**Recommended for most updates**

```bash
cd /opt/kna-history
./update.sh
```

**What it does:**
1. Creates automatic backup
2. Checks current version
3. Pulls new image
4. Restarts containers
5. Verifies health
6. Shows what changed

**Example Output:**
```
🔄 KNA History Update Script
====================================

📊 Current version: v1.0.0
📊 Latest version: v1.1.0

⚠️  Creating backup before update...
✅ Backup created: /data/backups/auto-20260207-120000.sql.gz

🔄 Pulling new image...
✅ Image pulled: ghcr.io/mark-me/kna-history:v1.1.0

🔄 Restarting services...
✅ Services restarted

⏳ Waiting for application to be healthy...
✅ Application is healthy!

📊 Update Summary:
   Previous: v1.0.0
   Current:  v1.1.0
   
🎉 Update completed successfully!
```

### 🔧 Method 2: Manual Update

**For advanced users or troubleshooting**

```bash
# 1. Backup
docker exec mariadb mysqldump -u root -p kna > backup_$(date +%Y%m%d).sql

# 2. Pull new image
docker compose pull kna-historie

# 3. Restart
docker compose up -d kna-historie

# 4. Verify
curl https://your-domain.com/health
docker compose logs -f kna-historie
```

### 🎯 Method 3: Specific Version

**Deploy specific version**

```bash
# Set version in .env
echo "KNA_IMAGE_TAG=v1.1.0" >> .env

# Update
docker compose pull
docker compose up -d

# Verify version
docker compose exec kna-historie python -c "from kna_data import __version__; print(__version__)"
```

## 🔄 Update Process Details

### 📦 Image Management

**Pull Latest:**
```bash
docker pull ghcr.io/mark-me/kna-history:latest
```

**Pull Specific Version:**
```bash
docker pull ghcr.io/mark-me/kna-history:v1.1.0
```

**List Available Tags:**
```bash
# Via GitHub API
curl https://api.github.com/repos/mark-me/kna-history/tags | jq '.[].name'
```

### 🔁 Container Restart

**Graceful Restart:**
```bash
# Gives containers time to shut down properly
docker compose restart kna-historie
```

**Recreate Container:**
```bash
# Forces recreation with new image
docker compose up -d --force-recreate kna-historie
```

**No Downtime Restart (Advanced):**
```bash
# Start new container before stopping old
docker compose up -d --no-deps --scale kna-historie=2
sleep 10
docker compose up -d --no-deps --scale kna-historie=1
```

### ✅ Health Verification

**After update, verify:**

```bash
# Check all containers running
docker compose ps

# Check health endpoint
curl https://your-domain.com/health
# Should return: {"status":"healthy","database":"connected"}

# Check logs for errors
docker compose logs --tail=50 kna-historie

# Test database connection
docker compose exec kna-historie python -c "
from kna_data import KnaDataReader
from kna_data.config import get_config
reader = KnaDataReader(config=get_config())
print('✅ Database connection OK')
"

# Test admin login
# Navigate to /auth/login and verify you can log in
```

## 🔙 Rollback Procedures

### ⚠️ When to Rollback

- Application fails health checks
- Database errors persist
- Critical functionality broken
- Performance severely degraded
- Data corruption detected

### 🔙 Quick Rollback

**Using update.sh backup:**

```bash
# Rollback to previous version
./update.sh rollback

# Or manually:
# 1. Stop services
docker compose down

# 2. Restore from automatic backup
LATEST_BACKUP=$(ls -t /data/backups/auto-*.sql.gz | head -1)
gunzip < $LATEST_BACKUP | docker exec -i mariadb mysql -u root -p kna

# 3. Use previous image tag
docker compose pull ghcr.io/mark-me/kna-history:v1.0.0
echo "KNA_IMAGE_TAG=v1.0.0" >> .env

# 4. Restart
docker compose up -d

# 5. Verify
curl https://your-domain.com/health
```

### 🔧 Rollback with Data Loss

**If database changes can't be reverted:**

```bash
# 1. Stop services
docker compose down

# 2. Restore from last good backup
gunzip < /data/backups/manual-20260206.sql.gz | \
  docker exec -i mariadb mysql -u root -p kna

# 3. Rollback to previous version
echo "KNA_IMAGE_TAG=v1.0.0" >> .env
docker compose pull
docker compose up -d

# 4. Inform users of data loss window
```

## 📊 Version Management

### 🏷️ Version Tags

**Format:** `vMAJOR.MINOR.PATCH`

**Examples:**
- `v1.0.0` - Initial release
- `v1.0.1` - Patch release (bug fix)
- `v1.1.0` - Minor release (new features)
- `v2.0.0` - Major release (breaking changes)

**Tag Aliases:**
- `latest` - Latest stable release
- `v1` - Latest v1.x.x
- `v1.1` - Latest v1.1.x

### 📈 Tracking Versions

**Check Current Version:**

```bash
# Via Docker image
docker compose images kna-historie

# Via application
docker compose exec kna-historie python -c "
from kna_data import __version__
print(f'Version: {__version__}')
"

# Via Git (if cloned from repo)
git describe --tags
```

**Version History:**
```bash
# List installed versions
docker images ghcr.io/mark-me/kna-history --format "{{.Tag}}"

# Remove old images
docker image prune -a
```

## 🔄 Database Migrations

### 📊 Migration Handling

**Check for Migrations:**
```bash
# Read release notes
# Look for "Database Changes" or "Migrations" section
```

**Run Migrations (if needed):**

Some updates may include database schema changes:

```bash
# Via CLI (if migration script provided)
docker compose exec kna-historie python manage.py migrate

# Or manually (SQL provided in release notes)
docker exec -i mariadb mysql -u root -p kna < migration.sql
```

### ⚠️ Breaking Database Changes

For major updates with schema changes:

1. **Backup first** (critical!)
2. **Test migration** in staging
3. **Schedule maintenance** window
4. **Run migration** scripts
5. **Verify data** integrity
6. **Keep backup** for 30 days

## 📝 Update Logs

### 📋 Keeping Track

**Log Updates:**

```bash
# Create update log
cat >> /var/log/kna-history-updates.log << EOF
$(date): Updated from v1.0.0 to v1.1.0
- Backup: /data/backups/auto-20260207-120000.sql.gz
- Duration: 5 minutes
- Issues: None
- Rollback: Not needed
EOF
```

**Review History:**
```bash
cat /var/log/kna-history-updates.log
```

### 📊 Monitoring After Update

**First 24 hours:**
- Monitor error logs closely
- Check resource usage
- Verify backup integrity
- Test critical functionality
- Monitor user feedback

**First week:**
- Review performance metrics
- Check for memory leaks
- Monitor disk usage growth
- Verify backup schedule working

## 🔔 Update Notifications

### 📧 Email Notifications

**Setup Notifications:**

```bash
# Configure email in update.sh
EMAIL_NOTIFY="admin@example.com"

# Notifications sent for:
# - Update started
# - Update completed
# - Update failed
# - Rollback performed
```

### 📱 Monitoring Integration

**Uptime Monitors:**
- UptimeRobot
- Pingdom
- Better Uptime

Configure to alert on:
- Health check failures
- Downtime during update
- Slow response times

## 🛠️ Special Update Scenarios

### 🔄 Updating from Very Old Version

**Multiple version jump (e.g., v1.0.0 → v2.0.0):**

```bash
# 1. Read ALL release notes between versions
# 2. Check for cumulative breaking changes
# 3. Update in stages if major changes
# 4. Extended testing recommended

# Example staged update:
./update.sh v1.5.0  # First to latest v1.x
# Test thoroughly
./update.sh v2.0.0  # Then to v2.0.0
```

### 🆕 First-Time Update

**Initial update from v1.0.0:**

```bash
# 1. Verify current working state
./status.sh

# 2. Create manual backup
docker exec mariadb mysqldump -u root -p kna | gzip > first-backup.sql.gz

# 3. Use update script
./update.sh

# 4. Extra verification
# - Test all major features
# - Check all pages load
# - Verify uploads work
# - Test admin functions
```

### 🔧 Hotfix Updates

**Critical security patches:**

```bash
# 1. Review security advisory
# 2. Pull specific hotfix version
docker pull ghcr.io/mark-me/kna-history:v1.0.1-hotfix

# 3. Quick backup
docker exec mariadb mysqldump -u root -p kna | gzip > hotfix-backup.sql.gz

# 4. Apply immediately
docker compose up -d

# 5. Verify fix applied
# Check version includes hotfix tag
```

## 📅 Maintenance Windows

### ⏰ Planning Downtime

**Recommended Window:**
- **Duration:** 30-60 minutes
- **Time:** Late night / early morning
- **Day:** Weekend or low-traffic day

**Notification Timeline:**
1. **7 days before:** Initial notification
2. **24 hours before:** Reminder
3. **1 hour before:** Final warning
4. **During maintenance:** Status page
5. **After completion:** Completion notice

### 📣 User Communication

**Maintenance Notice Template:**

```
Subject: KNA History - Scheduled Maintenance

Dear KNA History users,

We will be performing a system update:

📅 Date: Sunday, February 10, 2026
🕐 Time: 02:00 - 03:00 CET
⏱️ Duration: Approximately 1 hour

What to expect:
- Application unavailable during update
- No data loss
- Improved performance and features

What you can do:
- Save any ongoing work before 02:00
- Bookmark important pages
- Resume normal use after 03:00

Questions? Contact: admin@kna-hillegom.nl

Thank you for your patience!
```

## ✅ Post-Update Checklist

### 🔍 Verification Steps

- [ ] All containers running
- [ ] Health endpoint returns OK
- [ ] Database connection working
- [ ] Can log in as admin
- [ ] Can view performances list
- [ ] Can view member list
- [ ] Media files display
- [ ] Thumbnails load
- [ ] Search functionality works
- [ ] Upload test file (admin)
- [ ] No errors in logs
- [ ] SSL certificate valid
- [ ] Backup successful
- [ ] Monitoring active

### 📊 Performance Check

```bash
# Response time test
time curl -s https://your-domain.com/health

# Database query performance
docker compose exec mariadb mysql -u root -p -e "
SHOW VARIABLES LIKE 'slow_query_log';
SELECT COUNT(*) FROM kna.uitvoering;
"

# Resource usage
docker stats --no-stream kna-historie

# Disk usage
df -h /data
```

## 🆘 Troubleshooting Updates

### ❌ Update Fails

**Symptom:** Update script fails

**Solutions:**
```bash
# Check logs
docker compose logs kna-historie

# Verify image pulled
docker images | grep kna-history

# Check disk space
df -h

# Manual restart
docker compose restart kna-historie
```

### ❌ Application Won't Start

**Symptom:** Container exits immediately

**Solutions:**
```bash
# Check logs
docker compose logs kna-historie

# Verify configuration
./validate-config.sh

# Check database
docker compose ps mariadb

# Try rollback
./update.sh rollback
```

### ❌ Database Connection Issues

**Symptom:** Health check fails with database error

**Solutions:**
```bash
# Verify MariaDB running
docker compose ps mariadb

# Check credentials
docker compose exec kna-historie env | grep MARIADB

# Test connection
docker compose exec mariadb mysql -u root -p -e "SHOW DATABASES;"

# Restart MariaDB
docker compose restart mariadb
```

## 📚 Related Documentation

- [Configuration](configuration.md) - Configuration options
- [Backup](backup.md) - Backup procedures
- [Monitoring](monitoring.md) - Health monitoring
- [Troubleshooting](troubleshooting.md) - Common issues
- [Production](production.md) - Production setup
