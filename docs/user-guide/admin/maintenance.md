![Onderhoud](../../images/maintenance.png){ align=right width="90" }

# Onderhoud

Deze handleiding legt uit hoe je onderhouds taken uitvoert op het KNA Historie archief.

## Overzicht Onderhoudstaken

| Taak | Frequentie | Duur | Prioriteit |
|------|------------|------|------------|
| Thumbnails regenereren | Maandelijks | 10-30 min | Normaal |
| Database optimaliseren | Wekelijks | 2-5 min | Normaal |
| Cache legen | Bij problemen | < 1 min | Laag |
| Logs roteren | Maandelijks | 2-5 min | Normaal |
| Backup maken | Dagelijks (auto) | 5-15 min | **Hoog** |
| Disk cleanup | Maandelijks | 5-10 min | Normaal |

## Thumbnails

### Waarom Thumbnails?

Thumbnails zijn kleine versies van foto's:
- ⚡ **Sneller laden** van galerijen
- 💾 **Minder bandbreedte** voor gebruikers
- 📱 **Beter op mobiel** apparaten
- 🖼️ **Betere UX** bij browsen

### Automatisch Genereren

Bij elke data upload worden automatisch thumbnails gegenereerd:

**Proces:**
1. Excel met data uploaden
2. Systeem vindt alle foto's
3. Maakt thumbnails (300x300px)
4. Opslaan in `/thumbnails/` submap

**Ondersteunde formaten:**
- `.jpg`, `.jpeg`
- `.png`
- `.gif` (eerste frame)
- `.webp`

### Handmatig Regenereren

**Wanneer nodig:**
- Na direct uploaden van foto's (zonder Excel)
- Bij corrupte thumbnails
- Na wijzigen foto resolutie
- Bij ontbrekende thumbnails

**Stappen:**
1. Ga naar **Admin** → **Onderhoud**
2. Sectie **Thumbnails**
3. Klik **Regenereer Alle Thumbnails**
4. Wacht tot proces compleet

**Voortgang:**
```
🖼️ Thumbnails regenereren...

📁 annie_2015/        : 45/45 ✅
📁 faust_2018/        : 78/78 ✅
📁 grease_2020/       : 123/123 ✅
...

✅ Klaar! 3.298 thumbnails gegenereerd
⏱️ Duur: 12 minuten
```

### Instellingen

**Aanpassen thumbnail kwaliteit:**

**Admin** → **Instellingen** → **Media**

| Instelling | Standaard | Bereik |
|------------|-----------|--------|
| Breedte | 300px | 150-500px |
| Hoogte | 300px | 150-500px |
| Kwaliteit | 95% | 70-100% |
| Formaat | JPEG | JPEG/PNG/WebP |

!!! tip "Optimale Settings"
    - **Groot archief**: 200x200px, 85% kwaliteit
    - **Hoge kwaliteit**: 400x400px, 95% kwaliteit
    - **Mobiel optimaal**: 250x250px, 80% kwaliteit

### Problemen Oplossen

#### "Thumbnail generatie mislukt"

**Mogelijke oorzaken:**
- Schijf vol
- Geen schrijfrechten
- Corrupt bronbestand
- Geheugen tekort

**Oplossing:**
```bash
# Check schijfruimte
df -h /data/resources

# Fix permissies
sudo chown -R 1000:1000 /data/resources
sudo chmod -R 755 /data/resources/*/thumbnails

# Verwijder corrupte thumbnails
find /data/resources -name "thumbnails" -type d -exec rm -rf {} +

# Regenereer
```

#### "Sommige thumbnails ontbreken"

**Controleer:**
1. **Admin** → **Onderhoud** → **Thumbnail Status**
2. Zie welke mappen incomplete zijn
3. Klik **Regenereer Ontbrekende**

## Database Onderhoud

### Database Optimaliseren

**Waarom optimaliseren:**
- 🚀 Snellere queries
- 💾 Minder schijfruimte
- 🔧 Gefragmenteerde tables herstellen
- 📊 Update statistieken

**Uitvoeren:**
1. **Admin** → **Onderhoud** → **Database**
2. Klik **Optimaliseer Database**
3. Wacht (1-5 minuten)

**Proces:**
```sql
OPTIMIZE TABLE lid;
OPTIMIZE TABLE uitvoering;
OPTIMIZE TABLE rol;
OPTIMIZE TABLE file;
OPTIMIZE TABLE file_leden;
OPTIMIZE TABLE media_type;
OPTIMIZE TABLE users;
```

!!! note "Beste Tijdstip"
    Optimaliseer buiten piekuren (nachts/vroege ochtend).
    Database is tijdens proces readonly.

### Database Statistieken

Bekijk database gezondheid:

**Admin** → **Onderhoud** → **Database Status**

**Informatie:**
- 📊 **Tabel groottes** (in MB)
- 🔢 **Aantal rijen** per tabel
- 📈 **Groei trend** (laatste maand)
- ⚠️ **Fragmentatie** niveau
- 🔍 **Index status**

**Acties:**
- **Details**: Toon tabel structuur
- **Optimaliseer**: Optimaliseer specifieke tabel
- **Analyseer**: Uitgebreide analyse

### Integriteit Check

Controleer data integriteit:

1. **Admin** → **Onderhoud** → **Integriteit**
2. Klik **Check Database**

**Controles:**
- ✅ Referentiële integriteit (foreign keys)
- ✅ Ontbrekende media bestanden
- ✅ Orphaned records
- ✅ Duplicate entries
- ✅ Data types consistency

**Output:**
```
✅ Referentiële integriteit: OK
⚠️ 12 rollen verwijzen naar niet-bestaand lid
⚠️ 45 bestanden niet gevonden op disk
✅ Geen duplicates gevonden
```

### Cleanup

Verwijder oude/ongebruikte data:

**Admin** → **Onderhoud** → **Cleanup**

**Opties:**
- 🗑️ **Orphaned records**: Data zonder relaties
- 📁 **Ongebruikte bestanden**: Files niet in database
- 🖼️ **Oude thumbnails**: Van verwijderde foto's
- 📜 **Oude logs**: >90 dagen
- 💾 **Cache**: Alle gecachte data

!!! warning "Voorzichtig"
    Cleanup is permanent! Maak eerst backup.

## Cache Beheer

### Cache Legen

**Wanneer:**
- Na configuratie wijzigingen
- Bij vreemde weergave problemen
- Na data updates
- Bij prestatie problemen

**Uitvoeren:**
1. **Admin** → **Onderhoud** → **Cache**
2. Selecteer cache type:
   - **Application cache**: Python/Flask cache
   - **Template cache**: Jinja2 templates
   - **Browser cache**: Statische bestanden
   - **Database cache**: Query resultaten
3. Klik **Cache Legen**

**Effect:**
- ⚡ Volgende request iets langzamer
- 🔄 Nieuwe data direct zichtbaar
- 🐛 Problemen vaak opgelost

### Cache Statistieken

Zie cache gebruik:

**Informatie:**
- 📊 Hit ratio (hoe vaak cache gebruikt)
- 💾 Grootte in geheugen
- 🔢 Aantal items
- ⏱️ Gemiddelde leeftijd

**Optimaal:**
- Hit ratio: >80%
- Grootte: <500 MB
- Items: Varieert

## Logs

### Log Types

Het systeem houdt verschillende logs bij:

| Type | Locatie | Inhoud | Retentie |
|------|---------|--------|----------|
| **Application** | `/logs/app.log` | Flask errors & info | 30 dagen |
| **Access** | `/logs/access.log` | HTTP requests | 14 dagen |
| **Database** | `/logs/db.log` | Query logs | 7 dagen |
| **Audit** | Database | Admin acties | Permanent |

### Logs Bekijken

**Via Dashboard:**
1. **Admin** → **Onderhoud** → **Logs**
2. Selecteer log type
3. Filter op niveau/datum
4. Bekijk entries

**Levels:**
- 🔴 **ERROR**: Fouten die aandacht vereisen
- 🟡 **WARNING**: Potentiële problemen
- 🔵 **INFO**: Algemene informatie
- ⚪ **DEBUG**: Gedetailleerde debug info

**Via Command Line:**
```bash
# Laatste 100 regels
docker compose logs --tail=100 kna-historie

# Follow mode (real-time)
docker compose logs -f kna-historie

# Alleen errors
docker compose logs kna-historie | grep ERROR

# Specifieke tijdsperiode
docker compose logs --since="2026-02-06T10:00:00" kna-historie
```

### Log Rotatie

Automatische rotatie voorkomt volle disk:

**Configuratie:**
```yaml
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

**Handmatige rotatie:**
```bash
# Archiveer huidige logs
sudo mv /logs/app.log /logs/app.log.$(date +%Y%m%d)

# Comprimeer oude logs
sudo gzip /logs/*.log.20*

# Verwijder oude archives (>90 dagen)
find /logs -name "*.gz" -mtime +90 -delete
```

## Backup & Restore

### Automatische Backups

**Schema:**
- ⏰ **Tijd**: Dagelijks om 02:00 uur
- 📦 **Wat**: Database + configuratie
- 💾 **Waar**: `/data/backups/`
- 🔄 **Retentie**: 30 dagen

**Overzicht backups:**
1. **Admin** → **Onderhoud** → **Backups**
2. Zie lijst van backups
3. Check grootte en datum

### Handmatige Backup

**Via Dashboard:**
1. **Admin** → **Onderhoud** → **Backup**
2. Selecteer wat te backuppen:
   - ☑️ KNA Database
   - ☑️ Users Database
   - ☑️ Configuratie
   - ☑️ Media (optioneel, groot!)
3. Klik **Backup Nu**
4. Download backup

**Via Command Line:**
```bash
# Database backup
docker exec mariadb mysqldump -u root -p kna > kna_backup_$(date +%Y%m%d).sql

# Comprimeren
gzip kna_backup_*.sql

# Media backup
tar -czf media_backup_$(date +%Y%m%d).tar.gz /data/resources

# Complete backup
./backup.sh full
```

### Restore

**Via Dashboard:**
1. **Admin** → **Onderhoud** → **Restore**
2. Upload backup bestand
3. Selecteer componenten:
   - Database
   - Configuratie
   - Media
4. Klik **Herstellen**
5. Bevestig (onomkeerbaar!)

**Via Command Line:**
```bash
# Stop applicatie
docker compose down kna-historie

# Restore database
gunzip < kna_backup_20260206.sql.gz | \
  docker exec -i mariadb mysql -u root -p kna

# Restore media
tar -xzf media_backup_20260206.tar.gz -C /

# Start applicatie
docker compose up -d kna-historie
```

!!! danger "Restore Overschrijft Data"
    Restore vervangt ALLE huidige data!
    Maak eerst backup van huidige staat.

### Backup Testen

Test backups regelmatig:

**Maandelijks:**
1. Download recente backup
2. Restore op test omgeving
3. Verificeer data klopt
4. Test applicatie werkt
5. Documenteer resultaat

**Checklist:**
- ✅ Backup compleet
- ✅ Restore succesvol
- ✅ Data intact
- ✅ Media aanwezig
- ✅ Applicatie functioneel

## Disk Space Management

### Ruimte Controleren

**Dashboard:**
- **Admin** → **Onderhoud** → **Disk Space**
- Zie gebruik per categorie:
  - Database
  - Media (originelen)
  - Thumbnails
  - Logs
  - Backups

**Command Line:**
```bash
# Totaal overzicht
df -h

# Per directory
du -sh /data/*

# Grootste bestanden
du -ah /data/resources | sort -rh | head -20
```

### Ruimte Vrijmaken

**Bij weinig ruimte (<20%):**

1. **Verwijder oude thumbnails** en regenereer
   ```bash
   find /data/resources -name "thumbnails" -type d -exec rm -rf {} +
   ```

2. **Comprimeer oude backups**
   ```bash
   gzip /data/backups/*.sql
   ```

3. **Roteer logs**
   ```bash
   find /logs -name "*.log" -mtime +30 -delete
   ```

4. **Cleanup oude Docker images**
   ```bash
   docker image prune -a -f
   ```

5. **Archiveer oude media** (optioneel)
   - Verplaats zeer oude foto's naar archive
   - Houd alleen thumbnails online
   - Originelen op externe opslag

!!! warning "Voorzichtig met Verwijderen"
    - Maak altijd eerst backup
    - Verwijder niet zomaar media
    - Check wat je verwijdert
    - Test na cleanup

## Monitoring

### Health Checks

**Automatische Checks:**
- 🟢 **Database**: Connectie en response tijd
- 🟢 **Disk**: Beschikbare ruimte
- 🟢 **Memory**: RAM gebruik
- 🟢 **Services**: Docker containers status

**Dashboard Widget:**
```
Systeem Status
├── Database      : 🟢 Connected (23ms)
├── Disk Space    : 🟡 45% gebruikt (55GB vrij)
├── Memory        : 🟢 2.1 GB / 4 GB
└── Application   : 🟢 Healthy
```

**Endpoint:**
```bash
# HTTP health check
curl http://localhost:5000/health

# Response
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### Alerts

**Email Notificaties:**
- 🔴 Database connectie mislukt
- 🔴 Disk >90% vol
- 🟡 Backup ouder dan 7 dagen
- 🟡 Memory >80% gebruikt
- 🟡 Veel errors in logs

**Configureer:**
1. **Admin** → **Instellingen** → **Notificaties**
2. Voer email adres in
3. Selecteer alert types
4. Stel drempelwaarden in

### Status Script

Gebruik het `status.sh` script:

```bash
# Uitgebreide status
./status.sh

# Output:
========================================
KNA History - System Status
========================================

1. Docker Status:
  ✅ Docker is running
     Version: 24.0.7

2. Container Status:
  NAME           STATUS         PORTS
  kna-historie   Up 2 days      5000/tcp
  mariadb        Up 2 days      3306/tcp
  nginx          Up 2 days      80/tcp, 443/tcp

3. Application Health:
  Container: ✅ Running
  Health:    ✅ healthy
  Version:   1.0.0
  Uptime:    2d 14h 23m

4. MariaDB Status:
  Container: ✅ Running
  Database:  ✅ Responding
  Size:      2.34 GB

...
```

## Scheduled Tasks

### Cron Jobs

Automatische taken via cron:

```cron
# /etc/crontab

# Dagelijkse backup (02:00)
0 2 * * * root /opt/kna-history/backup.sh daily

# Wekelijkse optimalisatie (zondag 03:00)
0 3 * * 0 root /opt/kna-history/optimize-db.sh

# Maandelijkse cleanup (1e van maand, 04:00)
0 4 1 * * root /opt/kna-history/cleanup.sh

# Log rotatie (dagelijks 05:00)
0 5 * * * root /opt/kna-history/rotate-logs.sh
```

### Task Monitoring

Check of taken zijn uitgevoerd:

1. **Admin** → **Onderhoud** → **Scheduled Tasks**
2. Zie geschiedenis van taken
3. Controleer status en output

**Per taak:**
- ⏰ Laatste run
- ✅/❌ Status (success/failed)
- ⏱️ Duur
- 📝 Output/errors

## Performance

### Performance Metrics

**Dashboard:**
- ⚡ Response tijd queries
- 📊 Requests per minuut
- 💾 Database pool gebruik
- 🖥️ CPU/Memory gebruik

### Optimalisatie Tips

**Database:**
- Index op veelgebruikte kolommen
- Optimaliseer zware queries
- Gebruik connection pooling
- Regelmatig OPTIMIZE TABLE

**Media:**
- Gebruik thumbnails
- Lazy loading van afbeeldingen
- CDN voor statische bestanden
- Comprimeer grote bestanden

**Application:**
- Cache template renders
- Minify CSS/JS
- Gzip compressie
- Browser caching headers

## Troubleshooting

### Veelvoorkomende Problemen

#### "Database connectie mislukt"

```bash
# Check MariaDB status
docker compose ps mariadb

# Check logs
docker compose logs mariadb

# Restart
docker compose restart mariadb
```

#### "Disk vol"

```bash
# Ruimte vrijmaken
docker system prune -a
find /logs -mtime +30 -delete
rm -rf /data/resources/*/thumbnails
```

#### "Applicatie traag"

```bash
# Restart services
docker compose restart

# Check resources
docker stats

# Optimize database
docker exec mariadb mysqloptimize kna
```

## Volgende Stappen

- [Terug naar dashboard](dashboard.md)
- [Data uploaden](data-upload.md)
- [Gebruikers beheren](user-management.md)
