# KNA History - Deployment Guide

This directory contains all Docker and deployment configuration for the KNA History application.

## 📁 Directory Structure

```
deploy/
├── app/
│   └── Dockerfile                    # Main application Dockerfile
├── nginx/
│   ├── Dockerfile                    # Nginx reverse proxy
│   ├── nginx-https.conf.template     # Nginx HTTPS configuration
│   └── nginx-entrypoint.sh           # Nginx startup script
├── certbot-initial/
│   ├── Dockerfile                    # Initial certificate acquisition
│   └── certbot-initial-entrypoint.sh # Certbot initial run script
├── certbot-auto/
│   ├── Dockerfile                    # Automatic certificate renewal
│   └── certbot-auto-entrypoint.sh    # Certbot renewal script
├── docker-compose.yml                # Main production stack
├── docker-compose.certbot-initial.yml # Initial certificate setup
├── .env.example                      # Environment variables template
├── setup-certificates.sh             # First-time certificate setup
├── start.sh                          # Start the application
├── update.sh                         # Update to latest version
├── build-local.sh                    # Build images locally
└── README.md                         # This file
```

## 🚀 Quick Start

### First-Time Setup

1. **Configure environment variables**
   ```bash
   cd deploy
   cp .env.example .env
   nano .env  # Edit with your values
   ```

2. **Obtain SSL certificates** (one-time setup)
   ```bash
   ./setup-certificates.sh
   ```

3. **Start the application**
   ```bash
   ./start.sh
   ```

4. **Access your application**
   - HTTPS: `https://your-domain.duckdns.org`

### Updating to Latest Version

When a new version is released (or pushed to test):

```bash
./update.sh
```

This will:
- Pull the latest image from GitHub Container Registry
- Restart the application with zero downtime
- Show you the new version running

## 🔄 CI/CD with GitHub Actions

### Automatic Builds

The repository includes two GitHub Actions workflows:

#### 1. Test Branch (`test`)
- **Trigger**: Push to `test` branch
- **Image tags**: `ghcr.io/mark-me/kna-history:test`, `ghcr.io/mark-me/kna-history:test-<commit-sha>`
- **Use case**: Development testing

```bash
# Deploy test version
cd deploy
# Update docker-compose.yml to use :test tag
docker compose pull
docker compose up -d
```

#### 2. Release Tags (`v*.*.*`)
- **Trigger**: Push version tag (e.g., `v1.0.0`)
- **Image tags**: 
  - `ghcr.io/mark-me/kna-history:v1.0.0` (exact version)
  - `ghcr.io/mark-me/kna-history:1.0` (minor version)
  - `ghcr.io/mark-me/kna-history:1` (major version)
  - `ghcr.io/mark-me/kna-history:latest`
- **Use case**: Production releases

### Creating a Release

```bash
# Commit your changes
git add .
git commit -m "feat: new feature"

# Create and push a version tag
git tag v1.0.0
git push origin main --tags

# GitHub Actions will automatically:
# 1. Build the Docker image
# 2. Push to ghcr.io with multiple tags
# 3. Create a GitHub release with notes
```

### Pull Latest Release on Server

```bash
cd deploy
./update.sh
```

## 🛠️ Development

### Local Building

To build images locally for testing:

```bash
cd deploy
./build-local.sh v0.0.1-dev    # Build with custom version
./build-local.sh local --push   # Build and push to registry
```

### Testing Changes Locally

1. Make changes to your application code
2. Build locally: `./build-local.sh test-local`
3. Update `docker-compose.yml` to use your local tag
4. Restart: `docker compose up -d`

## 📋 Environment Variables

Copy `.env.example` to `.env` and configure:

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DOMAIN_NAME` | Your domain name | `kna-historie.duckdns.org` |
| `EMAIL_ADDRESS` | Email for Let's Encrypt | `admin@example.com` |
| `FLASK_SECRET` | Flask secret key | Generate with `openssl rand -hex 32` |
| `MARIADB_DATABASE` | Database name | `kna` |
| `MARIADB_USER` | Database user | `kna` |
| `MARIADB_PASSWORD` | Database password | Strong password |
| `MARIADB_ROOT_PASSWORD` | Database root password | Strong password |
| `DUCKDNS_SUBDOMAIN` | DuckDNS subdomain | `kna-historie` |
| `DUCKDNS_TOKEN` | DuckDNS API token | Your token from duckdns.org |
| `DIR_RESOURCES` | Host path for resources | `/data/kna_resources` |
| `DIR_MARIADB` | Host path for database | `/data/mariadb` |

### Generating Secure Secrets

```bash
# Generate Flask secret
openssl rand -hex 32

# Generate database password
openssl rand -base64 32
```

## 🔒 SSL/TLS Certificates

### Initial Setup

The first time you deploy, you need to obtain SSL certificates:

```bash
./setup-certificates.sh
```

This runs Certbot in standalone mode to obtain certificates from Let's Encrypt.

### Automatic Renewal

Once the main stack is running, the `certbot-auto` service automatically:
- Checks for certificate renewal every minute
- Renews certificates when they're close to expiration (Let's Encrypt sends reminder emails)
- Nginx automatically reloads every 6 hours to pick up renewed certificates

### Manual Renewal (if needed)

```bash
docker compose exec certbot-auto certbot renew --force-renewal
docker compose restart nginx
```

## 📊 Service Architecture

```
┌─────────────┐
│   DuckDNS   │  Dynamic DNS updates
└──────┬──────┘
       │
┌──────▼──────┐
│    Nginx    │  Reverse proxy + SSL termination
│   Port 443  │
└──────┬──────┘
       │
┌──────▼──────┐
│ kna-historie│  Flask application
│   Port 5000 │
└──────┬──────┘
       │
┌──────▼──────┐
│   MariaDB   │  Database
│   Port 3306 │
└─────────────┘

Certbot-Auto: Runs in background for certificate renewal
```

## 🔍 Useful Commands

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f kna-historie
docker compose logs -f nginx
docker compose logs -f mariadb

# Last 100 lines
docker compose logs --tail=100 kna-historie
```

### Service Management
```bash
# Check status
docker compose ps

# Restart a service
docker compose restart kna-historie

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ destroys data)
docker compose down -v
```

### Database Access
```bash
# MySQL shell
docker compose exec mariadb mysql -u root -p

# Backup database
docker compose exec mariadb mysqldump -u root -p kna > backup.sql

# Restore database
docker compose exec -T mariadb mysql -u root -p kna < backup.sql
```

### Container Shell Access
```bash
# App container
docker compose exec kna-historie bash

# Database container
docker compose exec mariadb bash

# Nginx container
docker compose exec nginx sh
```

## 🚨 Troubleshooting

### Application won't start

1. Check logs: `docker compose logs -f kna-historie`
2. Check database is healthy: `docker compose ps mariadb`
3. Verify environment variables: `docker compose config`

### SSL certificate errors

1. Check certificate exists: `ls -la /data/certbot/conf/live/your-domain/`
2. Check certbot logs: `docker compose logs certbot-auto`
3. Verify port 80 is accessible (for renewal)
4. Re-run setup: `./setup-certificates.sh`

### Database connection issues

1. Check MariaDB is running: `docker compose ps mariadb`
2. Test connection: `docker compose exec mariadb mysql -u kna -p kna`
3. Check credentials in `.env` file
4. Check network: `docker network ls`

### Can't pull latest image

1. Ensure you're logged into ghcr.io:
   ```bash
   echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
   ```
2. Verify image exists: `https://github.com/mark-me/kna-history/pkgs/container/kna-history`
3. Check permissions on the package

## 📝 Maintenance

### Regular Tasks

- **Daily**: Monitor logs for errors
- **Weekly**: Check disk space (`df -h`)
- **Monthly**: Review certificate expiry (auto-renewed, but check email)
- **Quarterly**: Update base images and dependencies

### Backups

```bash
# Backup database
./backup-database.sh

# Backup resources
tar -czf resources-backup-$(date +%Y%m%d).tar.gz /data/kna_resources/

# Backup certificates
tar -czf certbot-backup-$(date +%Y%m%d).tar.gz /data/certbot/
```

## 🤝 Contributing

When making changes to deployment configuration:

1. Test locally first
2. Update this README if needed
3. Create PR with description of changes
4. After merge to `main`, create a release tag

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## 📄 License

See main repository LICENSE file.
