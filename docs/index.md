# KNA Historie Documentatie

Welkom bij de documentatie van het KNA Historie archief systeem.

![KNA Historie](images/favicon.png){ width="100" }

## Wat is KNA Historie?

KNA Historie is een self-hosted web applicatie voor het beheren en tonen van het historisch archief van toneelgroep KNA Hillegom. Het systeem biedt:

- 📸 **Media beheer** - Foto's, video's en documenten van alle voorstellingen
- 👥 **Ledenbeheer** - Overzicht van alle (oud-)leden en hun rollen
- 🎭 **Voorstellingen** - Chronologisch overzicht van alle uitvoeringen
- 📅 **Tijdlijn** - Interactieve tijdlijn van de verenigingsgeschiedenis
- 🔐 **Beheer** - Admin interface voor data upload en gebruikersbeheer

## Documentatie Overzicht

Deze documentatie is opgesplitst in verschillende secties:

### 👤 Voor Gebruikers

Documentatie voor dagelijks gebruik van de applicatie:

- **[Introductie](user-guide/introduction.md)** - Overzicht van de applicatie
- **[Navigatie](user-guide/navigation.md)** - Door het archief bladeren
- **[Zoeken](user-guide/searching.md)** - Leden en voorstellingen vinden
- **[Media bekijken](user-guide/viewing-media.md)** - Foto's en video's bekijken

### 👨‍💼 Voor Beheerders

Documentatie voor administratieve taken:

- **[Admin Dashboard](user-guide/admin/dashboard.md)** - Overzicht van het admin panel
- **[Data Uploaden](user-guide/admin/data-upload.md)** - Excel bestanden uploaden
- **[Gebruikersbeheer](user-guide/admin/user-management.md)** - Gebruikers aanmaken en beheren
- **[Onderhoud](user-guide/admin/maintenance.md)** - Thumbnails regenereren en database beheer

### 💻 Voor Developers

Technische documentatie voor ontwikkelaars:

- **[Architectuur](developer-guide/architecture.md)** - Systeem overzicht
- **[Development Setup](developer-guide/setup.md)** - Lokale ontwikkelomgeving
- **[Configuration](developer-guide/configuration.md)** - Configuratie systeem
- **[Database Schema](developer-guide/database.md)** - Database structuur
- **[API Reference](developer-guide/api-reference.md)** - Code documentatie
- **[Debugging](developer-guide/debugging/quick-start.md)** - Debug handleidingen

### 🚀 Deployment

Documentatie voor deployment en operationele zaken:

- **[Quick Start](deployment/quick-start.md)** - Snelle deployment handleiding
- **[Production Setup](deployment/production.md)** - Productie deployment
- **[Configuration](deployment/configuration.md)** - Omgevingsvariabelen en settings
- **[Updates](deployment/updates.md)** - Applicatie updaten
- **[Backup & Restore](deployment/backup.md)** - Data backup strategieën
- **[Troubleshooting](deployment/troubleshooting.md)** - Veelvoorkomende problemen

## Quick Links

### 🚀 Aan de slag

- Nieuw bij KNA Historie? Start met de [Introductie](user-guide/introduction.md)
- Wil je de applicatie deployen? Zie [Quick Start Guide](deployment/quick-start.md)
- Developer? Bekijk de [Development Setup](developer-guide/setup.md)

### 📚 Veelgevraagd

- [Hoe upload ik nieuwe data?](user-guide/admin/data-upload.md)
- [Hoe maak ik een nieuwe gebruiker aan?](user-guide/admin/user-management.md)
- [Hoe update ik de applicatie?](deployment/updates.md)
- [Hoe debug ik de applicatie?](developer-guide/debugging/quick-start.md)

## Versie Informatie

- **Huidige versie**: 1.0.0
- **Python versie**: 3.13
- **Framework**: Flask
- **Database**: MariaDB
- **Container**: Docker

## Support

Voor vragen of problemen:

1. Raadpleeg eerst de [Troubleshooting Guide](deployment/troubleshooting.md)
2. Check de [GitHub Issues](https://github.com/mark-me/kna-history/issues)
3. Maak een nieuw issue aan op GitHub

## Licentie

Dit project is ontwikkeld voor KNA Hillegom.

---

**Laatste update**: {{ git_revision_date_localized }}
