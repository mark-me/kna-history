# Admin Dashboard

Het admin dashboard geeft beheerders toegang tot alle beheerfuncties van het KNA Historie archief.

## Toegang tot Admin Panel

### Inloggen

1. Ga naar `/auth/login`
2. Voer je **gebruikersnaam** in
3. Voer je **wachtwoord** in
4. Klik op **Inloggen**

!!! warning "Alleen voor Beheerders"
    Het admin panel is alleen toegankelijk voor gebruikers met de rol 'admin'.
    Gewone viewers hebben geen toegang tot deze functies.

### Eerste Keer Inloggen

Bij een nieuwe installatie:

- **Gebruikersnaam**: `admin`
- **Wachtwoord**: Wat je hebt ingesteld in `ADMIN_PASSWORD`

!!! danger "Verander Standaard Wachtwoord"
    Wijzig het standaard admin wachtwoord direct na eerste login!
    Ga naar je profiel en kies een sterk wachtwoord.

## Dashboard Overzicht

Het dashboard toont:

### 📊 Statistieken

**Database Statistieken**
- 👥 **Aantal leden**: Totaal aantal (oud-)leden in database
- 🎭 **Aantal voorstellingen**: Totaal aantal uitvoeringen
- 🎬 **Aantal rollen**: Totaal aantal gespeelde rollen
- 📸 **Aantal mediabestanden**: Foto's, video's, documenten
- 📁 **Totale opslag**: Gebruikt schijfruimte

**Recente Activiteit**
- Laatst geüploade data
- Nieuwste media bestanden
- Recente wijzigingen
- Laatst aangemelde gebruikers

### ⚡ Snelacties

Directe toegang tot veelgebruikte functies:

| Actie | Beschrijving |
|-------|--------------|
| 📤 **Upload Data** | Excel bestand uploaden |
| 👥 **Gebruikers** | Gebruikers beheren |
| 🖼️ **Thumbnails** | Regenereer thumbnails |
| 📊 **Statistieken** | Gedetailleerde statistieken |
| ⚙️ **Instellingen** | Systeem configuratie |

## Hoofdfuncties

### 1. Data Beheer

**Excel Upload**
- [Nieuwe data uploaden](data-upload.md)
- Validatie van bestand
- Preview voor import
- Rollback mogelijkheden

**Database**
- Huidige data bekijken
- Export naar Excel
- Database optimaliseren
- Backup maken

### 2. Gebruikersbeheer

**Gebruikers**
- [Nieuwe gebruikers aanmaken](user-management.md)
- Wachtwoorden resetten
- Rollen toewijzen
- Gebruikers deactiveren

**Rollen**
- **Admin**: Volledige toegang
- **Viewer**: Alleen bekijken

### 3. Media Beheer

**Thumbnails**
- [Regenereer alle thumbnails](maintenance.md#thumbnails)
- Verwijder oude thumbnails
- Kwaliteit instellingen

**Opslag**
- Bekijk schijfruimte
- Verwijder ongebruikte bestanden
- Comprimeer grote bestanden

### 4. Systeem

**Monitoring**
- Systeem status
- Database connectie
- Schijfruimte
- Fouten logboek

**Onderhoud**
- Cache legen
- Logs roteren
- Database optimaliseren
- Backup taken

## Navigatie in Admin Panel

### Hoofdmenu

```
Admin Dashboard
│
├── 📊 Dashboard (overzicht)
│
├── 📤 Upload
│   ├── Valideren
│   └── Importeren
│
├── 👥 Gebruikers
│   ├── Overzicht
│   ├── Nieuw
│   └── Bewerken
│
├── 🔧 Onderhoud
│   ├── Thumbnails
│   ├── Database
│   └── Cache
│
└── ⚙️ Instellingen
    ├── Systeem
    ├── Media
    └── Beveiliging
```

### Breadcrumbs

Volg je pad door het admin panel:

```
Dashboard > Gebruikers > Gebruiker Bewerken > Jan de Vries
```

Klik op elk deel om terug te navigeren.

## Rechten en Rollen

### Admin Rechten

Als admin kun je:

- ✅ Alle data bekijken en wijzigen
- ✅ Excel bestanden uploaden
- ✅ Gebruikers aanmaken en beheren
- ✅ Systeeminstellingen wijzigen
- ✅ Onderhoudstaken uitvoeren
- ✅ Logs inzien
- ✅ Backups maken

### Viewer Rechten

Viewers kunnen:

- ✅ Door archief bladeren
- ✅ Media bekijken
- ✅ Zoeken in data
- ❌ **Geen** admin functies
- ❌ **Geen** data wijzigen
- ❌ **Geen** uploads

## Dashboard Widgets

### Activiteit Widget

Toont recente activiteit:

- ⬆️ **Uploads**: Laatst geüploade data
- 👤 **Logins**: Wie heeft ingelogd
- 📝 **Wijzigingen**: Wat is aangepast
- ⚠️ **Fouten**: Eventuele problemen

### Statistieken Widget

Visuele grafieken van:

- 📈 **Groei**: Toename van media per jaar
- 👥 **Leden**: Actieve vs. inactieve leden
- 🎭 **Voorstellingen**: Per type en decennium
- 📸 **Media**: Verdeling foto/video/document

### Systeem Status Widget

Realtime systeem informatie:

| Indicator | Status |
|-----------|--------|
| 🟢 Database | Connected |
| 🟢 Schijfruimte | 45% gebruikt |
| 🟢 Geheugen | 2.1 GB / 4 GB |
| 🟡 Thumbnails | 85% gegenereerd |

**Status Kleuren:**
- 🟢 **Groen**: Alles OK
- 🟡 **Geel**: Aandacht vereist
- 🔴 **Rood**: Actie nodig

### Snelle Taken Widget

Veelgebruikte acties:

```
[📤 Upload Excel]  [👥 Nieuwe Gebruiker]
[🖼️ Regenereer Thumbnails]  [💾 Backup Nu]
```

## Meldingen

### Systeem Meldingen

Beheerders ontvangen meldingen over:

**Success** ✅
- Upload succesvol
- Gebruiker aangemaakt
- Backup voltooid

**Warning** ⚠️
- Schijfruimte <20%
- Niet alle thumbnails gegenereerd
- Oude backup (>7 dagen)

**Error** ❌
- Database connectie mislukt
- Upload gefaald
- Bestand niet gevonden

### Melding Centrum

Toegang via bel-icoon (🔔):

- **Ongelezen**: Rode stip met aantal
- **Archief**: Oude meldingen
- **Instellingen**: Welke meldingen ontvangen

## Shortcuts

Sneltoetsen voor admin panel:

| Toets | Actie |
|-------|-------|
| `Ctrl+U` | Upload pagina |
| `Ctrl+Shift+U` | Gebruikers |
| `Ctrl+D` | Terug naar dashboard |
| `Ctrl+/` | Zoek in admin panel |
| `Ctrl+Shift+T` | Thumbnails regenereren |

## Beveiliging

### Sessie Beheer

**Auto-logout**
- Na 60 minuten inactiviteit
- Bij sluiten browser (optioneel)
- Handmatig uitloggen altijd mogelijk

**Sessie Informatie**
- Zie waar je bent ingelogd
- Verbreek andere sessies
- Bekijk login geschiedenis

### Two-Factor Authentication

Voor extra beveiliging (optioneel):

1. Ga naar **Profiel** → **Beveiliging**
2. Klik **2FA Activeren**
3. Scan QR code met authenticator app
4. Voer verificatie code in
5. Sla backup codes op

!!! tip "Aanbevolen voor Admins"
    Schakel 2FA in voor alle admin accounts.

### IP Whitelist

Beperk toegang tot specifieke IP adressen:

1. **Instellingen** → **Beveiliging**
2. Klik **IP Whitelist**
3. Voeg toegestane IP's toe
4. Activeer whitelist

!!! warning "Let Op"
    Je kunt jezelf buitensluiten! Test eerst met één IP.

## Audit Log

### Wijzigingen Traceren

Het systeem logt alle admin acties:

**Gelogde Acties**
- Data uploads
- Gebruiker wijzigingen
- Instellingen aanpassingen
- Verwijderingen

**Log Informatie**
- 👤 **Wie**: Welke gebruiker
- 🕐 **Wanneer**: Datum en tijd
- 📝 **Wat**: Welke actie
- 💻 **Waar**: IP adres

**Log Bekijken**
- **Onderhoud** → **Audit Log**
- Filter op gebruiker, actie, datum
- Export naar CSV

## Backup & Restore

### Automatische Backups

Het systeem maakt dagelijks backups:

- 🕐 **Tijd**: 02:00 uur 's nachts
- 📦 **Inhoud**: Database + instellingen
- 💾 **Locatie**: `/data/backups/`
- 🔄 **Retentie**: 30 dagen

### Handmatige Backup

Maak op elk moment een backup:

1. **Dashboard** → **Backup Nu**
2. Kies wat te backuppen:
   - ☑️ Database
   - ☑️ Instellingen
   - ☑️ Gebruikers
3. Klik **Backup Maken**
4. Download backup bestand

### Restore

Herstel uit backup:

1. **Onderhoud** → **Restore**
2. Upload backup bestand
3. Selecteer wat te herstellen
4. Bevestig (irreversible!)
5. Wacht tot restore compleet

!!! danger "Belangrijk"
    Restore overschrijft huidige data!
    Maak eerst een backup van huidige staat.

## Hulp en Support

### Help Functies

**In-app Help**
- **?** icoon op elke pagina
- Context-gevoelige hints
- Video tutorials
- Documentatie links

**Support Opties**
- 📖 [Volledige documentatie](../../index.md)
- 💬 Contact formulier
- 🐛 Bug rapportage
- 💡 Feature requests

### Veelgestelde Vragen

**"Ik kan niet inloggen"**
- Controleer gebruikersnaam en wachtwoord
- Capslock uit?
- Cookies toegestaan?
- Contact andere admin voor wachtwoord reset

**"Upload faalt"**
- Bekijk [Upload handleiding](data-upload.md)
- Valideer Excel bestand eerst
- Check bestandsgrootte (<50MB)
- Zie error logs voor details

**"Thumbnails worden niet gegenereerd"**
- Zie [Onderhoud handleiding](maintenance.md#thumbnails)
- Check schijfruimte
- Controleer bestandspermissies
- Regenereer handmatig

## Best Practices

### Dagelijks

- ✅ Check dashboard voor meldingen
- ✅ Bekijk systeem status
- ✅ Controleer foutmeldingen

### Wekelijks

- ✅ Bekijk upload logs
- ✅ Controleer schijfruimte
- ✅ Review gebruikers activiteit
- ✅ Update statistieken

### Maandelijks

- ✅ Backup maken en testen
- ✅ Gebruikers lijst opschonen
- ✅ Oude logs archiveren
- ✅ Systeem updates controleren

### Bij Problemen

1. ✅ Check systeem status
2. ✅ Bekijk error logs
3. ✅ Controleer documentatie
4. ✅ Test in development eerst
5. ✅ Maak backup voor grote wijzigingen

## Volgende Stappen

- [Leer data uploaden](data-upload.md) via Excel
- [Beheer gebruikers](user-management.md) en rollen
- [Onderhoud taken](maintenance.md) uitvoeren
