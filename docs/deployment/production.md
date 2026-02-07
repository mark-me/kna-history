# Production Deployment

Comprehensive guide for deploying KNA History in a production environment.

## 🏗️ Infrastructure Requirements

### 💻 Server Specifications

**Minimum:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 20 GB SSD
- Network: 10 Mbps

**Recommended:**
- CPU: 4 cores
- RAM: 4 GB
- Disk: 50 GB SSD
- Network: 100 Mbps

**Scaling for Large Archives:**
- CPU: 8 cores
- RAM: 8 GB
- Disk: 100+ GB SSD
- Network: 1 Gbps

### 🌐 Network Requirements

**Required Ports:**

| Port | Protocol | Purpose | Public |
|------|----------|---------|--------|
| 80 | TCP | HTTP (redirect to HTTPS) | Yes |
| 443 | TCP | HTTPS | Yes |
| 22 | TCP | SSH (admin only) | Limited |
| 3306 | TCP | MariaDB (internal only) | No |

**Firewall Configuration:**

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Check status
sudo ufw status
```

### 📁 Storage Layout

```
/data/
├── kna_resources/          # Media files (grows over time)
│   ├── performance_1/
│   ├── performance_2/
│   └── ...
├── mariadb/                # Database files
│   └── mysql/
├── certbot/                # SSL certificates
│   ├── conf/
│   └── www/
└── backups/                # Backup storage
    ├── daily/
    ├── weekly/
    └── monthly/
```

## 🔧 Production Setup

### 🐳 Docker Installation

```bash
# Remove old versions
sudo apt-get remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt-get update
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER

# Verify installation
docker --version
docker compose version
```

### 🗂️ Directory Structure

```bash
# Create production directories
sudo mkdir -p /data/{kna_resources,mariadb,certbot/{conf,www},backups/{daily,weekly,monthly}}

# Set ownership
sudo chown -R 1000:1000 /data/kna_resources
sudo chown -R 999:999 /data/mariadb
sudo chown -R root:root /data/certbot
sudo chown -R root:root /data/backups

# Set permissions
sudo chmod 755 /data
sudo chmod 755 /data/kna_resources
sudo chmod 700 /data/mariadb
sudo chmod 755 /data/certbot
sudo chmod 700 /data/backups
```

### 📦 Application Deployment

```bash
# Create application directory
sudo mkdir -p /opt/kna-history
cd /opt/kna-history

# Download latest release
wget https://github.com/mark-me/kna-history/releases/latest/download/kna-history.tar.gz
tar -xzf kna-history.tar.gz

# Or clone repository
git clone https://github.com/mark-me/kna-history.git .
git checkout tags/v1.0.0  # Use specific version

# Set ownership
sudo chown -R root:root /opt/kna-history
sudo chmod +x /opt/kna-history/*.sh
```

## 🔐 Security Hardening

### 🛡️ System Security

**Update System:**
```bash
# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Enable automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

**SSH Hardening:**
```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Recommended settings:
Port 22                          # Or custom port
PermitRootLogin no
PasswordAuthentication no        # Use SSH keys only
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Restart SSH
sudo systemctl restart sshd
```

**Fail2Ban:**
```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local

# Add:
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600

# Start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 🔒 Application Security

**Environment File:**
```bash
# Secure .env file
sudo chmod 600 /opt/kna-history/.env
sudo chown root:root /opt/kna-history/.env
```

**Generate Strong Secrets:**
```python
# Generate SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(48))"

# Generate database passwords
python3 -c "import secrets; print('MARIADB_PASSWORD=' + secrets.token_urlsafe(24))"
python3 -c "import secrets; print('MARIADB_ROOT_PASSWORD=' + secrets.token_urlsafe(24))"

# Generate admin password
python3 -c "import secrets; print('ADMIN_PASSWORD=' + secrets.token_urlsafe(16))"
```

**Docker Security:**
```bash
# Run Docker in rootless mode (optional, advanced)
dockerd-rootless-setuptool.sh install

# Limit container resources
# Edit docker-compose.yml:
services:
  kna-historie:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 🌍 Domain & SSL Setup

### 📝 DNS Configuration

**DuckDNS Setup:**
```bash
# Install DuckDNS client
mkdir -p ~/duckdns
cd ~/duckdns

# Create update script
cat > duck.sh << 'EOF'
#!/bin/bash
echo url="https://www.duckdns.org/update?domains=YOUR_DOMAIN&token=YOUR_TOKEN&ip=" | curl -k -o ~/duckdns/duck.log -K -
EOF

chmod +x duck.sh

# Test
./duck.sh
cat duck.log  # Should show "OK"

# Add to cron (every 5 minutes)
crontab -e
*/5 * * * * ~/duckdns/duck.sh >/dev/null 2>&1
```

**Or use Docker container:**
```yaml
# In docker-compose.yml (already included)
duckdns:
  image: ghcr.io/linuxserver/duckdns
  environment:
    - SUBDOMAINS=${DUCKDNS_SUBDOMAIN}
    - TOKEN=${DUCKDNS_TOKEN}
```

### 🔐 SSL Certificates

**Let's Encrypt with Certbot:**
```bash
# Initial certificate
./setup-certificates.sh

# Auto-renewal (already configured in certbot-auto container)
# Certificates renew automatically every 60 days
```

**Manual certificate renewal:**
```bash
docker compose run --rm certbot renew
docker compose restart nginx
```

**Check certificate expiry:**
```bash
openssl x509 -in /data/certbot/conf/live/YOUR_DOMAIN/cert.pem \
  -noout -enddate
```

## 🚀 Deployment Process

### 📋 Pre-Deployment Checklist

- [ ] Server meets minimum requirements
- [ ] Domain DNS configured and propagated
- [ ] Firewall rules configured
- [ ] Data directories created with correct permissions
- [ ] `.env` file configured with strong secrets
- [ ] Configuration validated (`./validate-config.sh`)
- [ ] SSH access secured (key-based, no root)
- [ ] Backup strategy planned

### 🎬 Deployment Steps

**1. Pull Docker Images:**
```bash
cd /opt/kna-history
docker compose pull
```

**2. Obtain SSL Certificates:**
```bash
./setup-certificates.sh
```

**3. Start Services:**
```bash
./start.sh
```

**4. Verify Deployment:**
```bash
# Check all services
./status.sh

# Test health endpoint
curl https://your-domain.com/health

# Check logs
docker compose logs -f kna-historie
```

**5. Initial Admin Login:**
```
URL: https://your-domain.com/auth/login
Username: admin
Password: [from ADMIN_PASSWORD in .env]
```

**6. Upload Initial Data:**
- Navigate to Admin → Upload
- Upload Excel file with historical data
- Validate and import

### 🔄 Zero-Downtime Updates

For updates with minimal downtime:

```bash
# 1. Pull new image
docker pull ghcr.io/mark-me/kna-history:latest

# 2. Tag current as backup
docker tag ghcr.io/mark-me/kna-history:latest \
           ghcr.io/mark-me/kna-history:backup-$(date +%Y%m%d)

# 3. Update container
docker compose up -d kna-historie

# 4. Verify
curl https://your-domain.com/health

# 5. Rollback if needed (see update.sh)
```

## 📊 Resource Optimization

### 💾 Database Tuning

**MariaDB Configuration:**

Create `mariadb.cnf`:
```ini
[mysqld]
# InnoDB settings
innodb_buffer_pool_size = 1G      # 50-80% of RAM
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# Query cache
query_cache_size = 64M
query_cache_type = 1

# Connections
max_connections = 100

# Logging (disable in production for performance)
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2
```

Mount in docker-compose.yml:
```yaml
mariadb:
  volumes:
    - ./mariadb.cnf:/etc/mysql/conf.d/custom.cnf:ro
```

### 🖼️ Media Optimization

**Thumbnail Generation:**
```bash
# Configure thumbnail quality
# In Admin → Settings → Media
Thumbnail Size: 300x300
Quality: 85%
Format: JPEG
```

**Storage Optimization:**
```bash
# Compress old media
find /data/kna_resources -name "*.jpg" -mtime +365 \
  -exec jpegoptim --size=2000k {} \;

# Archive very old performances
tar -czf archive_2000s.tar.gz /data/kna_resources/2000_*
mv archive_2000s.tar.gz /data/backups/archives/
```

### 🚀 Nginx Optimization

**Nginx Configuration:**

Edit nginx config for caching:
```nginx
# Gzip compression
gzip on;
gzip_vary on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

# Browser caching
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Static files
location /static/ {
    alias /app/static/;
    expires 1y;
}
```

## 🔍 Monitoring Setup

### 📈 Health Checks

**Uptime Monitoring:**
```bash
# Install monitoring script
./monitor.sh

# Add to cron (every 5 minutes)
crontab -e
*/5 * * * * /opt/kna-history/monitor.sh
```

**External Monitoring:**
- [UptimeRobot](https://uptimerobot.com/) - Free tier available
- [Pingdom](https://www.pingdom.com/)
- [Better Uptime](https://betteruptime.com/)

Configure to check:
- `https://your-domain.com/health` every 5 minutes
- Alert via email/SMS on failure

### 📊 Log Aggregation

**Configure log rotation:**
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/kna-history

# Add:
/opt/kna-history/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker compose restart kna-historie > /dev/null
    endscript
}
```

**Centralized Logging (Optional):**
```yaml
# docker-compose.yml
services:
  kna-historie:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 💾 Backup Strategy

### 🗄️ Automated Backups

See detailed [Backup Guide](backup.md) for complete backup strategy.

**Quick Setup:**
```bash
# Add to crontab
crontab -e

# Daily database backup at 2 AM
0 2 * * * /opt/kna-history/backup.sh daily

# Weekly full backup on Sunday at 3 AM
0 3 * * 0 /opt/kna-history/backup.sh weekly
```

### 🔄 Disaster Recovery

**Recovery Plan:**
1. Restore from latest backup
2. Verify database integrity
3. Regenerate thumbnails if needed
4. Test application functionality

See [Backup & Restore Guide](backup.md) for procedures.

## 📈 Scaling

### ⚖️ Load Balancing

For high-traffic deployments:

```yaml
# docker-compose.yml
services:
  kna-historie-1:
    # ... config
  
  kna-historie-2:
    # ... config
  
  nginx:
    # ... load balancer config
```

### 💾 Database Replication

For high availability:

**Master-Slave setup:**
```yaml
mariadb-master:
  # ... master config

mariadb-slave:
  # ... slave config with replication
```

### 📁 External Storage

For large media archives:

**S3-compatible storage:**
```python
# Update config to use S3
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
```

## 🆘 Troubleshooting

See [Troubleshooting Guide](troubleshooting.md) for comprehensive solutions.

**Quick Checks:**
```bash
# System resources
./status.sh

# Application logs
docker compose logs -f kna-historie

# Database status
docker exec mariadb mysqladmin ping

# Disk space
df -h

# Memory usage
free -h
```

## 📚 Next Steps

- **[Configuration Guide](configuration.md)** - Detailed environment variables
- **[Updates](updates.md)** - Update procedures and best practices
- **[Backup](backup.md)** - Comprehensive backup strategy
- **[Monitoring](monitoring.md)** - Advanced monitoring setup
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## ✅ Production Checklist

### Initial Setup
- [ ] Server provisioned and secured
- [ ] Docker installed and configured
- [ ] Directories created with correct permissions
- [ ] Environment variables configured
- [ ] Secrets generated and secured
- [ ] Domain DNS configured
- [ ] SSL certificates obtained
- [ ] Firewall rules applied

### Security
- [ ] SSH hardened (key-based, no root)
- [ ] Fail2ban configured
- [ ] Automatic security updates enabled
- [ ] `.env` file permissions set to 600
- [ ] Strong passwords used everywhere
- [ ] Admin password changed after first login

### Operational
- [ ] Application deployed and running
- [ ] Health checks passing
- [ ] Backups configured and tested
- [ ] Monitoring set up
- [ ] Log rotation configured
- [ ] Update procedure documented
- [ ] Disaster recovery plan created
- [ ] Team trained on procedures
