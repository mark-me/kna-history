# Snelstart Installatie

Zet KNA History in productie in minder dan 30 minuten.

## 🎯 Vereisten

Zorg vóór je begint voor het volgende:

- ✅ **Linux-server** (Ubuntu 20.04+ or Debian 11+)
- ✅ **Root or sudo toegang**
- ✅ **Domeinnaam** die naar jouw server wijst
- ✅ **E-mailadres** voor SSL-certificaten
- ✅ **Minimaal 2GB RAM** aanbevolen
- ✅ **Minimaal 10 GB schijfruimte** (meer bij veel media)

## 🚀 Installatiestappen

### 📥 Stap 1: Installeer Docker

```bash
# Installeer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Voeg je gebruiker toe aan de docker-groep
sudo usermod -aG docker $USER

# Installeer Docker Compose plugin
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Controleer installatie
docker --version
docker compose version
```

### 📂 Stap 2: Maak mappen aan

```bash
# Maak datamappen
sudo mkdir -p /data/kna_resources
sudo mkdir -p /data/mariadb
sudo mkdir -p /data/certbot/conf
sudo mkdir -p /data/certbot/www

# Stel rechten in
sudo chown -R 1000:1000 /data/kna_resources
sudo chown -R 999:999 /data/mariadb
```

### 📋 Stap 3: Download bestanden

```bash
# Maak applicatiemap
mkdir -p ~/kna-history
cd ~/kna-history

# Download docker-compose.yml en scripts
# (Vanuit jouw repository of release)
wget https://github.com/mark-me/kna-history/releases/latest/download/deploy.tar.gz
tar -xzf deploy.tar.gz
```

### ⚙️ Stap 4: Configureer omgeving

```bash
# Kopieer voorbeeld
cp env.example .env

# Bewerk configuratie
nano .env
```

**Verplichte aanpassingen in `.env`:**

```bash
# Genereer veilige SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")

# Jouw domein
DOMAIN_NAME=kna-historie.duckdns.org
EMAIL_ADDRESS=your-email@example.com

# Genereer database-wachtwoorden
MARIADB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")
MARIADB_ROOT_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(24))")

# Stel admin-wachtwoord in
ADMIN_PASSWORD=YourStrongPassword123!

# Update DATABASE_URL met jouw MARIADB_PASSWORD
DATABASE_URL=mysql+mysqldb://kna:YOUR_MARIADB_PASSWORD@mariadb/kna_users

# DuckDNS (indien gebruikt)
DUCKDNS_SUBDOMAIN=your-subdomain
DUCKDNS_TOKEN=your-token
```

### ✅ Stap 5: Valideer configuratie

```bash
# Maak scripts uitvoerbaar
chmod +x *.sh

# Valideer configuratie
./validate-config.sh
```

Verwachte uitvoer:

```bash
✅ Configuratie is geldig en klaar voor gebruik!
```

### 🔐 Stap 6: Verkrijg SSL-certificaten

```bash
# Stel SSL-certificaten in
./setup-certificates.sh
```

Dit script:

1. Stopt tijdelijk services op poort 80
2. Draait certbot om certificaten op te halen
3. Slaat certificaten op in `/data/certbot/conf`

**Let op:** Je domein moet al naar het IP-adres van je server wijzen!

### 🎬 Stap 7: Start de applicatie

```bash
# Start alle services
./start.sh
```

Dit commando:

1. Haalt Docker-images op
2. Start containers
3. Controleert gezondheid
4. Toont status

### 🎉 Stap 8: Controleer de installatie

```bash
# Bekijk status
./status.sh

# Of handmatig
curl https://jouw-domein.nl/health
```

Verwachte reactie:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

## 🔑 Eerste login

1. Ga naar: https://jouw-domein.nl/auth/login
2. Gebruikersnaam:admin
3. Wachtwoord: Het ADMIN_PASSWORD dat je in .env hebt ingesteld

!!! waarschuwing "Verander direct het admin-wachtwoord"
  Wijzig het admin-wachtwoord onmiddellijk na de eerste login!

## 📊 Gegevens uploaden

Na inloggen:

1. Ga naar **Admin Dashboard**
2. Klik op **Gegevens uploaden**
3. Selecteer je Excel-bestand
4. Klik op **Valideren**
5. Controleer resultaten
6. Klik op **Importeren**

Zie [Gegevens upload handleiding](../user-guide/admin/data-upload.md) voor details over het Excel-formaat.

## 🎨 Optioneel: Media-bestanden uploaden

```bash
# Via SCP
scp -r /local/media/* user@server:/data/kna_resources/

# Via rsync
rsync -av /local/media/ user@server:/data/kna_resources/

# Stel rechten opnieuw in
sudo chown -R 1000:1000 /data/kna_resources
```

Genereer daarna thumbnails opnieuw:

1. Admin → Onderhoud
2. Klik op "Thumbnails opnieuw genereren"

## 📝 Na installatie

### 🔒 Security Checklist

- [ ] Standaard admin-wachtwoord gewijzigd
- [ ] Sterke wachtwoorden in `.env`
- [ ] `.env` bestand heeft rechten 600 (`chmod 600 .env`)
- [ ] Firewall ingesteld (ports 80, 443 open)
- [ ] SSH met sleutel-authenticatie ingeschakeld
- [ ] Regelmatige backups gepland

### 🔧 Automatische backups instellen

```bash
# Bewerk crontab
crontab -e

# Dagelijkse backup om 02:00
0 2 * * * cd /root/kna-history && ./backup.sh daily
```

### 📈 Monitoring instellen

```bash
# Test monitoring script
./status.sh

# Voeg toe aan cron voor meldingen
*/15 * * * * cd /root/kna-history && ./monitor.sh
```

## 🐛 Probleemoplossing

### ❌ "Certificate validation failed"

**Issue:** Domain not pointing to server

**Solution:**

```bash
# Check DNS
dig your-domain.com

# Should show your server's IP
# Wait for DNS propagation (up to 24 hours)
```

### ❌ "Database connection failed"

**Issue:** MariaDB not ready

**Solution:**

```bash
# Check MariaDB status
docker compose ps mariadb

# View logs
docker compose logs mariadb

# Restart if needed
docker compose restart mariadb
```

### ❌ "Port 80 already in use"

**Issue:** Another service using port 80

**Solution:**

```bash
# Find what's using port 80
sudo lsof -i :80

# Stop the service
sudo systemctl stop apache2  # or nginx, etc.
```

### ❌ "Permission denied on /data"

**Issue:** Wrong directory permissions

**Solution:**

```bash
# Fix permissions
sudo chown -R 1000:1000 /data/kna_resources
sudo chown -R 999:999 /data/mariadb
sudo chmod -R 755 /data
```

## 📚 Next Steps

- **[Production Setup](production.md)** - Advanced production configuration
- **[Configuration Guide](configuration.md)** - Detailed environment variables
- **[Backup Strategy](backup.md)** - Set up automated backups
- **[Monitoring](monitoring.md)** - Configure health monitoring
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions

## ⏱️ Quick Reference

### Common Commands

```bash
# Start services
./start.sh

# Check status
./status.sh

# View logs
docker compose logs -f kna-historie

# Update application
./update.sh

# Backup now
docker exec mariadb mysqldump -u root -p kna > backup.sql

# Restart service
docker compose restart kna-historie

# Stop all services
docker compose down
```

### Important Locations

| Path | Purpose |
|------|---------|
| `/data/kna_resources/` | Media files |
| `/data/mariadb/` | Database files |
| `/data/certbot/conf/` | SSL certificates |
| `~/kna-history/.env` | Configuration |
| `~/kna-history/*.sh` | Management scripts |

## 🆘 Getting Help

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review logs: `docker compose logs`
3. Run status check: `./status.sh`
4. Validate config: `./validate-config.sh`
5. Check [GitHub Issues](https://github.com/mark-me/kna-history/issues)

---

**Congratulations! 🎉** Your KNA History application is now running in production.
