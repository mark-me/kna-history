# KNA History - Deployment Guide

Complete guide for deploying and managing the KNA History application with the unified configuration system.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Configuration](#configuration)
4. [Deployment](#deployment)
5. [Management Scripts](#management-scripts)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

## Prerequisites

### Server Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB+ RAM recommended
- 10GB+ disk space (more for media files)
- Docker and Docker Compose installed
- Port 80 and 443 open for HTTP/HTTPS
- Port 3306 available for MariaDB (can be internal only)

### Domain Setup

- Domain name pointing to your server's IP (via DuckDNS or other DNS)
- Email address for SSL certificate notifications

### Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

## Initial Setup

### 1. Clone/Download the Application

```bash
# Clone the repository
git clone https://github.com/mark-me/kna-history.git
cd kna-history

# Or download and extract the release
wget https://github.com/mark-me/kna-history/releases/latest/download/kna-history.tar.gz
tar -xzf kna-history.tar.gz
cd kna-history
```

### 2. Create Data Directories

```bash
# Create directories for persistent data
sudo mkdir -p /data/kna_resources
sudo mkdir -p /data/mariadb
sudo mkdir -p /data/certbot/conf
sudo mkdir -p /data/certbot/www

# Set correct permissions
sudo chown -R 1000:1000 /data/kna_resources
sudo chown -R 999:999 /data/mariadb  # MariaDB container uses uid 999
```

### 3. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit configuration
nano .env
```

**Required changes in `.env`:**

```bash
# Generate a secure SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")

# Set your domain
DOMAIN_NAME=your-domain.duckdns.org
EMAIL_ADDRESS=your-email@example.com

# Generate secure database passwords
MARIADB_PASSWORD=<strong-random-password>
MARIADB_ROOT_PASSWORD=<strong-random-password>
ADMIN_PASSWORD=<strong-admin-password>

# Update DATABASE_URL with your MariaDB password
DATABASE_URL=mysql+mysqldb://kna:YOUR_MARIADB_PASSWORD@mariadb/kna_users

# DuckDNS configuration (if using DuckDNS)
DUCKDNS_SUBDOMAIN=your-subdomain
DUCKDNS_TOKEN=your-duckdns-token
```

**Generate secure passwords:**

```bash
# Generate random passwords
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(48))"
python3 -c "import secrets; print('MARIADB_PASSWORD=' + secrets.token_urlsafe(24))"
python3 -c "import secrets; print('MARIADB_ROOT_PASSWORD=' + secrets.token_urlsafe(24))"
python3 -c "import secrets; print('ADMIN_PASSWORD=' + secrets.token_urlsafe(16))"
```

### 4. Validate Configuration

```bash
# Make scripts executable (if not already)
chmod +x *.sh

# Validate your configuration
./validate-config.sh
```

This will check for:
- Missing required variables
- Weak/default passwords
- Directory permissions
- Docker installation
- SSL certificate status

## Configuration

### Environment Variables Reference

See [CONFIG_QUICK_REFERENCE.md](CONFIG_QUICK_REFERENCE.md) for detailed information about all configuration options.

### Key Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (DO NOT commit to git) |
| `docker-compose.yml` | Docker services configuration |
| `env.example` | Template for `.env` file |

### Configuration Classes

The application uses three configuration classes:

- **ProductionConfig**: For Docker deployment (default)
- **DevelopmentConfig**: For local development
- **TestingConfig**: For running tests

The active configuration is selected via `FLASK_ENV` or `KNA_ENV` environment variable.

## Deployment

### First-Time Deployment

#### Step 1: Obtain SSL Certificates

```bash
./setup-certificates.sh
```

This will:
1. Stop any services on port 80
2. Run certbot to obtain SSL certificates
3. Store certificates in `/data/certbot/conf`

**Note:** Your domain must already be pointing to your server's IP address.

#### Step 2: Start the Application

```bash
./start.sh
```

This will:
1. Validate configuration
2. Check for security issues
3. Create required directories
4. Pull latest Docker images
5. Start all services
6. Verify health

#### Step 3: Verify Deployment

```bash
# Check system status
./status.sh

# Or manually check
curl https://your-domain.duckdns.org/health

# View logs
docker compose logs -f kna-historie
```

#### Step 4: Access the Application

1. Navigate to: `https://your-domain.duckdns.org`
2. Login with admin credentials:
   - Username: `admin`
   - Password: `<value from ADMIN_PASSWORD in .env>`

### Updating the Application

```bash
./update.sh
```

This will:
1. Create a backup of the current image
2. Pull the latest version
3. Restart the application
4. Verify health
5. Show version changes

If issues occur, you can rollback (instructions shown in the script output).

## Management Scripts

### validate-config.sh

Validates your configuration before deployment.

```bash
./validate-config.sh
```

**Checks:**
- Required environment variables
- Security (password strength, default values)
- Database configuration
- Directory existence and permissions
- Docker installation
- SSL certificate status

**Exit codes:**
- 0: Configuration is valid
- 1: Configuration has errors (deployment will fail)

### start.sh

Starts the application with validation and health checks.

```bash
./start.sh
```

**Features:**
- Configuration validation
- Security warnings
- Directory creation
- Health verification
- Detailed status output

### update.sh

Updates the application to the latest version.

```bash
./update.sh
```

**Features:**
- Automatic backup creation
- Version tracking
- Health checks
- Rollback instructions
- Detailed logs

### status.sh

Shows comprehensive system status.

```bash
./status.sh
```

**Information shown:**
- Docker status
- Container status (all services)
- Application health
- Database status
- SSL certificate expiry
- Disk usage
- Resource usage (CPU/memory)
- Recent errors

### setup-certificates.sh

Obtains or renews SSL certificates.

```bash
./setup-certificates.sh
```

**Use cases:**
- Initial certificate setup
- Manual certificate renewal
- Certificate troubleshooting

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check configuration
./validate-config.sh

# Check logs
docker compose logs kna-historie

# Check if ports are in use
sudo lsof -i :5000
sudo lsof -i :80
sudo lsof -i :443

# Restart services
docker compose restart
```

#### 2. Database Connection Failed

```bash
# Check MariaDB is running
docker compose ps mariadb

# Check MariaDB logs
docker compose logs mariadb

# Test database connection
docker exec mariadb mysql -u root -p"$MARIADB_ROOT_PASSWORD" -e "SELECT 1"

# Verify DATABASE_URL in .env matches MARIADB_PASSWORD
```

#### 3. SSL Certificate Issues

```bash
# Check certificate status
openssl x509 -in /data/certbot/conf/live/$DOMAIN_NAME/cert.pem -text -noout | grep -A2 Validity

# Renew certificates
./setup-certificates.sh

# Check nginx is using correct certificates
docker exec nginx nginx -t
```

#### 4. Media Files Not Loading

```bash
# Check directory permissions
ls -la /data/kna_resources

# Fix permissions
sudo chown -R 1000:1000 /data/kna_resources

# Check volume mounting
docker inspect kna-historie | grep -A 10 Mounts

# Check DIR_RESOURCES and DIR_RESOURCES_HOST in .env
```

#### 5. Admin Login Fails

```bash
# Reset admin password by restarting (will recreate admin user)
docker compose restart kna-historie

# Or manually update in database
docker exec -it mariadb mysql -u root -p kna_users
```

### Debug Mode

Enable detailed logging:

```bash
# Edit .env
FLASK_ENV=development

# Restart
docker compose restart kna-historie

# View detailed logs
docker compose logs -f kna-historie
```

### Health Check Endpoint

```bash
# Check application health
curl http://localhost:5000/health

# Expected response:
# {"status":"healthy","database":"connected"}
```

## Maintenance

### Regular Tasks

#### Daily
- Monitor logs for errors: `docker compose logs -f`
- Check disk space: `df -h`

#### Weekly
- Check system status: `./status.sh`
- Review security updates
- Backup databases

#### Monthly
- Update application: `./update.sh`
- Review SSL certificate expiry
- Clean up old Docker images: `docker image prune -a`

### Backup Strategy

#### Database Backup

```bash
# Backup KNA data
docker exec mariadb mysqldump -u root -p"$MARIADB_ROOT_PASSWORD" kna > kna_backup_$(date +%Y%m%d).sql

# Backup users database
docker exec mariadb mysqldump -u root -p"$MARIADB_ROOT_PASSWORD" kna_users > kna_users_backup_$(date +%Y%m%d).sql

# Compress backups
gzip kna_backup_*.sql
gzip kna_users_backup_*.sql
```

#### Media Backup

```bash
# Backup resources directory
tar -czf kna_resources_backup_$(date +%Y%m%d).tar.gz -C /data kna_resources
```

#### Automated Backups

Create a cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/backup-script.sh
```

Example `backup-script.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/kna"
DATE=$(date +%Y%m%d)

mkdir -p $BACKUP_DIR

# Database backups
docker exec mariadb mysqldump -u root -p"$MARIADB_ROOT_PASSWORD" kna | gzip > $BACKUP_DIR/kna_$DATE.sql.gz
docker exec mariadb mysqldump -u root -p"$MARIADB_ROOT_PASSWORD" kna_users | gzip > $BACKUP_DIR/kna_users_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Database Restore

```bash
# Restore KNA data
gunzip < kna_backup_20260206.sql.gz | docker exec -i mariadb mysql -u root -p"$MARIADB_ROOT_PASSWORD" kna

# Restore users database
gunzip < kna_users_backup_20260206.sql.gz | docker exec -i mariadb mysql -u root -p"$MARIADB_ROOT_PASSWORD" kna_users
```

### Monitoring

Set up monitoring for:
- Application uptime
- Database availability
- Disk space
- SSL certificate expiry
- Error rates in logs

Example with simple monitoring script:

```bash
#!/bin/bash
# monitor.sh - Simple health monitoring

if ! curl -sf http://localhost:5000/health > /dev/null; then
    echo "Application is down!" | mail -s "KNA History Alert" admin@example.com
    docker compose restart kna-historie
fi
```

Add to crontab:
```bash
*/5 * * * * /path/to/monitor.sh
```

### Security Updates

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Update Docker images
docker compose pull
docker compose up -d

# Check for security advisories
docker scout cves ghcr.io/mark-me/kna-history:latest
```

### Log Rotation

Configure log rotation to prevent disk space issues:

```bash
# Create /etc/docker/daemon.json
sudo nano /etc/docker/daemon.json
```

Add:
```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

Restart Docker:
```bash
sudo systemctl restart docker
```

## Support Resources

- **Configuration Reference**: [CONFIG_QUICK_REFERENCE.md](CONFIG_QUICK_REFERENCE.md)
- **Migration Guide**: [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Configuration Documentation**: [CONFIG_README.md](CONFIG_README.md)
- **Status Check**: Run `./status.sh`
- **Validation**: Run `./validate-config.sh`

## Quick Reference Commands

```bash
# First-time setup
cp env.example .env              # Create configuration
nano .env                        # Edit configuration
./validate-config.sh            # Validate setup
./setup-certificates.sh         # Get SSL certificates
./start.sh                      # Start application

# Daily operations
./status.sh                     # Check system status
docker compose logs -f          # View logs
docker compose restart          # Restart all services

# Maintenance
./update.sh                     # Update application
docker compose pull             # Pull new images
docker image prune -a           # Clean up old images

# Troubleshooting
./validate-config.sh            # Check configuration
docker compose logs kna-historie # View app logs
docker compose ps               # Check containers
curl http://localhost:5000/health # Test health

# Backup
docker exec mariadb mysqldump -u root -p kna > backup.sql
tar -czf resources.tar.gz /data/kna_resources
```
