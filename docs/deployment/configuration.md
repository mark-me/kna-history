# Configuration Guide

Complete reference for all configuration options in KNA History deployment.

## 📋 Environment Variables

All configuration is done through environment variables in the `.env` file.

### 🔐 Security & Authentication

#### SECRET_KEY

**Purpose:** Flask session encryption and CSRF protection

**Required:** Yes

**Generation:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

**Example:**
```bash
SECRET_KEY=g8Kb9xvN3dP7mQ1wZ2fT4hL6jY8kR5sA0cV9bX3nM2uW1eR4t
```

**Security:**
- Minimum 32 characters (48+ recommended)
- Change if compromised
- Unique per environment
- Never commit to git

#### ADMIN_PASSWORD

**Purpose:** Default admin user password

**Required:** Yes

**Requirements:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers
- Special characters recommended

**Example:**
```bash
ADMIN_PASSWORD=Kna!Theater2026Secure
```

**Security:**
- Change immediately after first login
- Don't use default passwords
- Store securely (password manager)

### 🗄️ Database Configuration

#### MariaDB Settings

**MARIADB_HOST**

**Purpose:** Database server hostname

**Default:** `mariadb` (Docker service name)

**Values:**
```bash
# Production (Docker)
MARIADB_HOST=mariadb

# Development (local)
MARIADB_HOST=127.0.0.1:3306

# External server
MARIADB_HOST=db.example.com:3306
```

**MARIADB_USER**

**Purpose:** Database username

**Default:** `kna`

**Example:**
```bash
MARIADB_USER=kna
```

**MARIADB_PASSWORD**

**Purpose:** Database user password

**Required:** Yes

**Generation:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

**Example:**
```bash
MARIADB_PASSWORD=xK9mP2wQ8vL4nR7sT3fY6hJ1
```

**MARIADB_DATABASE**

**Purpose:** Database name for KNA data

**Default:** `kna`

**Example:**
```bash
MARIADB_DATABASE=kna
```

**MARIADB_ROOT_PASSWORD**

**Purpose:** MariaDB root user password

**Required:** Yes (for Docker container)

**Generation:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(24))"
```

**Example:**
```bash
MARIADB_ROOT_PASSWORD=aB3dE5gH7jK9mN2pQ4sT6vX8
```

#### Users Database

**DATABASE_URL**

**Purpose:** SQLAlchemy connection string for Flask-Login users

**Required:** Yes

**Format:**
```
{dialect}+{driver}://{username}:{password}@{host}/{database}
```

**Examples:**

=== "Production (MariaDB)"
    ```bash
    DATABASE_URL=mysql+mysqldb://kna:YOUR_PASSWORD@mariadb/kna_users
    ```

=== "Development (SQLite)"
    ```bash
    DATABASE_URL=sqlite:///dev.db
    ```

=== "PostgreSQL"
    ```bash
    DATABASE_URL=postgresql://kna:password@localhost/kna_users
    ```

**Creating Users Database:**
```sql
CREATE DATABASE kna_users;
GRANT ALL PRIVILEGES ON kna_users.* TO 'kna'@'%';
FLUSH PRIVILEGES;
```

### 📁 File Storage

#### DIR_RESOURCES

**Purpose:** Container path for media files

**Default:** `/data/resources/`

**Example:**
```bash
DIR_RESOURCES=/data/resources/
```

**Note:** This is the path **inside** the container.

#### DIR_RESOURCES_HOST

**Purpose:** Host path for media files (Docker volume)

**Required:** Yes

**Example:**
```bash
DIR_RESOURCES_HOST=/data/kna_resources
```

**Note:** This is the path on the **host** machine.

**Permissions:**
```bash
sudo mkdir -p /data/kna_resources
sudo chown -R 1000:1000 /data/kna_resources
sudo chmod 755 /data/kna_resources
```

#### DIR_MARIADB

**Purpose:** Host path for MariaDB data

**Required:** Yes

**Example:**
```bash
DIR_MARIADB=/data/mariadb
```

**Permissions:**
```bash
sudo mkdir -p /data/mariadb
sudo chown -R 999:999 /data/mariadb
sudo chmod 700 /data/mariadb
```

### 🌐 Domain & SSL

#### DOMAIN_NAME

**Purpose:** Your domain name for the application

**Required:** Yes (for SSL)

**Examples:**
```bash
DOMAIN_NAME=kna-historie.duckdns.org
DOMAIN_NAME=history.kna-hillegom.nl
DOMAIN_NAME=www.example.com
```

**Requirements:**
- Must point to your server's IP
- Can be subdomain or root domain
- Supports multiple domains (comma-separated)

#### EMAIL_ADDRESS

**Purpose:** Email for Let's Encrypt notifications

**Required:** Yes (for SSL)

**Example:**
```bash
EMAIL_ADDRESS=admin@kna-hillegom.nl
```

**Usage:**
- Certificate expiry notifications
- Let's Encrypt important updates
- Rate limit notifications

#### DuckDNS Configuration

**DUCKDNS_SUBDOMAIN**

**Purpose:** DuckDNS subdomain (without .duckdns.org)

**Required:** Only if using DuckDNS

**Example:**
```bash
DUCKDNS_SUBDOMAIN=kna-historie
```

**DUCKDNS_TOKEN**

**Purpose:** DuckDNS API token

**Required:** Only if using DuckDNS

**Example:**
```bash
DUCKDNS_TOKEN=12345678-1234-1234-1234-123456789abc
```

**Get token:** https://www.duckdns.org/

### ⚙️ Environment Selection

#### FLASK_ENV / KNA_ENV

**Purpose:** Select configuration environment

**Values:**
- `production` - Production settings
- `development` - Development settings
- `testing` - Testing settings

**Examples:**
```bash
# Production
FLASK_ENV=production

# Development
FLASK_ENV=development

# Alternative variable
KNA_ENV=production
```

**Effects:**

| Setting | Production | Development |
|---------|-----------|-------------|
| Debug | False | True |
| Auto-reload | No | Yes |
| Error detail | Generic | Full stack |
| Query logging | No | Yes |
| Users DB | MariaDB | SQLite |

## 📄 Configuration Files

### 🐳 docker-compose.yml

Main Docker Compose configuration.

**Key Sections:**

#### Services

```yaml
services:
  kna-historie:      # Main application
  mariadb:           # Database
  nginx:             # Web server
  certbot-auto:      # SSL renewal
  duckdns:           # Dynamic DNS (optional)
```

#### Environment Variables

All services use environment variables from `.env`:

```yaml
environment:
  FLASK_ENV: ${FLASK_ENV:-production}
  SECRET_KEY: ${SECRET_KEY}
  MARIADB_HOST: ${MARIADB_HOST}
  # ... etc
```

#### Volumes

```yaml
volumes:
  resources:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DIR_RESOURCES_HOST}
  
  mariadb:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: ${DIR_MARIADB}
```

#### Networks

```yaml
networks:
  kna-network:
    driver: bridge
```

### 🔧 Nginx Configuration

Located in `deploy/nginx/nginx.conf`

**HTTP to HTTPS Redirect:**
```nginx
server {
    listen 80;
    server_name ${DOMAIN_NAME};
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

**HTTPS Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name ${DOMAIN_NAME};
    
    ssl_certificate /etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:...;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://kna-historie:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 🔑 SSL Configuration

**Certbot Settings:**

In `deploy/certbot-auto/`:

```bash
# Renewal configuration
renew-hook=docker compose restart nginx
deploy-hook=docker compose restart nginx
```

**Certificate Locations:**
```
/data/certbot/conf/live/${DOMAIN_NAME}/
├── cert.pem           # Certificate
├── chain.pem          # Intermediate certificates
├── fullchain.pem      # Certificate + chain
└── privkey.pem        # Private key
```

## 🎛️ Advanced Configuration

### 🔧 Resource Limits

**Docker Compose:**

```yaml
services:
  kna-historie:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

**System Limits:**

```bash
# /etc/security/limits.conf
www-data soft nofile 65536
www-data hard nofile 65536
```

### 🗄️ MariaDB Tuning

**Custom Configuration:**

Create `mariadb.cnf`:

```ini
[mysqld]
# Performance
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Connections
max_connections = 100
wait_timeout = 600

# Query cache
query_cache_size = 64M
query_cache_type = 1

# Character set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Logging
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

**Mount in docker-compose.yml:**
```yaml
mariadb:
  volumes:
    - ./mariadb.cnf:/etc/mysql/conf.d/custom.cnf:ro
```

### 🚀 Performance Tuning

**Flask Settings:**

```python
# In config.py
class ProductionConfig(Config):
    # Werkzeug
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    # SQLAlchemy
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_PRE_PING = True
    
    # Upload limits
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
```

**Gunicorn Workers:**

```python
# gunicorn.conf.py
workers = 4                    # CPU cores * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
```

### 📊 Logging Configuration

**Log Levels:**

```yaml
# docker-compose.yml
kna-historie:
  environment:
    LOG_LEVEL: INFO
    
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
      labels: "service,environment"
```

**Python Logging:**

```python
# logging_kna.py
import logging

logger = logging.getLogger("KNA")
logger.setLevel(logging.INFO)

# Production: Only INFO and above
# Development: DEBUG and above
```

## 🔍 Configuration Validation

### ✅ Pre-Deployment Checks

Use the `validate-config.sh` script:

```bash
./validate-config.sh
```

**Validates:**
- ✅ Required variables present
- ✅ Password strength
- ✅ No default passwords
- ✅ Database URL format
- ✅ Directory permissions
- ✅ Docker availability
- ✅ Port availability
- ✅ SSL certificate status

### 🧪 Configuration Testing

**Test Database Connection:**
```bash
docker compose run --rm kna-historie python -c "
from kna_data.config import get_config
config = get_config()
engine = config.get_engine()
with engine.connect() as conn:
    conn.execute('SELECT 1')
print('✅ Database connection successful')
"
```

**Test Application Startup:**
```bash
docker compose up kna-historie
# Check logs for errors
docker compose logs kna-historie
```

## 🔄 Configuration Changes

### 🔄 Updating Configuration

**Process:**
1. Stop services: `docker compose down`
2. Edit `.env` file
3. Validate: `./validate-config.sh`
4. Start services: `docker compose up -d`

**Hot Reload (Limited):**

Some changes don't require restart:
- Media files
- Template changes
- Static files

Require restart:
- Environment variables
- Database settings
- Domain/SSL changes

### 🎯 Environment-Specific Configs

**Multiple Environments:**

```bash
# Production
cp .env.example .env.production
# Edit with production values

# Staging
cp .env.example .env.staging
# Edit with staging values

# Use specific env file
docker compose --env-file .env.production up -d
```

## 📚 Configuration Examples

### 🏢 Small Organization

```bash
# Resources
MARIADB_HOST=mariadb
DIR_RESOURCES_HOST=/data/kna_resources

# Performance (minimal)
# No additional tuning needed

# Backup
# Daily backups, 30 day retention
```

### 🎭 Large Archive

```bash
# Resources
MARIADB_HOST=mariadb
DIR_RESOURCES_HOST=/mnt/large_storage/kna_resources

# Performance
# mariadb.cnf: innodb_buffer_pool_size = 4G
# Gunicorn workers = 8

# Backup
# Hourly incremental, daily full
# 90 day retention, off-site storage
```

### 🔧 Development

```bash
FLASK_ENV=development
MARIADB_HOST=127.0.0.1:3306
DATABASE_URL=sqlite:///dev.db
DIR_RESOURCES=./data/resources/
SECRET_KEY=dev-secret-not-for-production
ADMIN_PASSWORD=admin123
```

### 🧪 Testing/Staging

```bash
FLASK_ENV=production
MARIADB_HOST=staging-db.internal
DATABASE_URL=mysql+mysqldb://kna:password@staging-db.internal/kna_users
DOMAIN_NAME=staging.kna-historie.org
# Use separate DuckDNS subdomain
```

## 🔐 Security Best Practices

### 🛡️ Secrets Management

**Never:**
- ❌ Commit `.env` to git
- ❌ Use default passwords
- ❌ Share secrets via email/chat
- ❌ Reuse passwords across environments

**Always:**
- ✅ Use strong, random secrets
- ✅ Rotate secrets regularly (90 days)
- ✅ Use password manager
- ✅ Encrypt backups containing secrets
- ✅ Limit access to `.env` file

**File Permissions:**
```bash
# .env file should be readable only by root
chmod 600 .env
chown root:root .env

# Verify
ls -la .env
# -rw------- 1 root root
```

### 🔒 Environment Isolation

**Separate secrets per environment:**

```bash
# Production
SECRET_KEY=prod_g8Kb9xvN3dP7mQ1wZ2fT4hL6jY8kR5sA

# Staging
SECRET_KEY=stag_xK9mP2wQ8vL4nR7sT3fY6hJ1dG5cH8

# Development
SECRET_KEY=dev_aB3cD4eF5gH6jK7mN8pQ9rS1tU2vW3
```

## 📋 Configuration Checklist

### ✅ Initial Setup

- [ ] `.env` file created from template
- [ ] All required variables set
- [ ] Strong secrets generated
- [ ] Database passwords unique
- [ ] Admin password secure
- [ ] Domain configured
- [ ] SSL certificates obtained
- [ ] File permissions correct (600 for .env)
- [ ] Configuration validated
- [ ] Test deployment successful

### ✅ Security Review

- [ ] No default passwords used
- [ ] SECRET_KEY is 48+ characters
- [ ] Database passwords are 24+ characters
- [ ] Admin password is 16+ characters
- [ ] `.env` not committed to git
- [ ] `.env` has 600 permissions
- [ ] Secrets stored in password manager
- [ ] Different secrets per environment

### ✅ Production Readiness

- [ ] FLASK_ENV=production
- [ ] DEBUG=False
- [ ] Valid DOMAIN_NAME
- [ ] SSL certificates active
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] Log rotation enabled
- [ ] Resource limits set
- [ ] Performance tuned

## 🆘 Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for configuration issues.

**Quick Checks:**

```bash
# Validate configuration
./validate-config.sh

# Check environment loading
docker compose config

# Verify database connection
docker compose run --rm kna-historie python -c "
from kna_data.config import get_config
print(get_config().mariadb_url)
"
```

## 📚 Related Documentation

- [Quick Start](quick-start.md) - Fast deployment guide
- [Production Setup](production.md) - Production deployment
- [Updates](updates.md) - Update procedures
- [Backup](backup.md) - Backup configuration
- [Monitoring](monitoring.md) - Monitoring setup
- [Troubleshooting](troubleshooting.md) - Common issues
