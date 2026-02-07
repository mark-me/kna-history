
![Upload](../../images/user-management.png){ align=right width="90" }

# Gebruikersbeheer

Deze handleiding legt uit hoe je gebruikers beheert in het KNA Historie archief.

## 👥 Gebruikersrollen

Het systeem kent twee rollen:

### 👑 Admin

Volledige toegang tot alle functies:

- ✅ Alle viewer rechten
- ✅ Data uploaden via Excel
- ✅ Gebruikers aanmaken en beheren
- ✅ Systeeminstellingen wijzigen
- ✅ Onderhoudstaken uitvoeren
- ✅ Logs en statistieken bekijken

### 👤 Viewer

Alleen-lezen toegang:

- ✅ Archief doorzoeken
- ✅ Voorstellingen bekijken
- ✅ Leden opzoeken
- ✅ Media bekijken en downloaden
- ❌ Geen admin functies
- ❌ Geen wijzigingen maken

## 📋 Gebruikers Overzicht

### Toegang tot Gebruikersbeheer

1. Log in als admin
2. Ga naar **Admin Dashboard**
3. Klik op **👥 Gebruikers**

### Gebruikerslijst

Het overzicht toont:

| Kolom | Beschrijving |
| ----- | ------------ |
| **Gebruikersnaam** | Inlognaam |
| **Email** | Email adres |
| **Rol** | Admin of Viewer |
| **Status** | Actief / Inactief |
| **Laatst ingelogd** | Laatste login datum |
| **Aangemaakt** | Wanneer account is aangemaakt |
| **Acties** | Bewerken / Verwijderen |

### Sorteren en Filteren

**Sorteer op:**

- Gebruikersnaam (A-Z)
- Laatst ingelogd
- Datum aangemaakt
- Rol

**Filter op:**

- 👑 Alleen admins
- 👤 Alleen viewers
- ✅ Alleen actieve gebruikers
- ❌ Alleen inactieve gebruikers

## ➕ Nieuwe Gebruiker Aanmaken

### Stap voor Stap

1. Klik op **➕ Nieuwe Gebruiker**
2. Vul het formulier in
3. Klik **Aanmaken**

### Formulier Velden

**Gebruikersnaam** *verplicht*

- Unieke naam voor inloggen
- 3-30 karakters
- Alleen letters, cijfers, underscore
- Voorbeeld: `jan_devries`, `p.janssen`

!!! tip "Naamgeving"
    Gebruik een consistent patroon:
    - `voornaam.achternaam`
    - `v.achternaam`
    - `initialen.achternaam`

**Email** *verplicht*

- Geldig email adres
- Moet uniek zijn
- Voor wachtwoord reset
- Voor notificaties

**Wachtwoord** *verplicht*

- Minimaal 8 karakters
- Hoofdletter, kleine letter, cijfer
- Speciaal teken aanbevolen
- Geen eenvoudige woorden

!!! warning "Sterk Wachtwoord"
    Voorbeelden van goede wachtwoorden:
    - ✅ `Kna!2026Theater`
    - ✅ `V00rst3ll!ng#23`
    - ❌ `password123`
    - ❌ `kna2026`

**Rol** *verplicht*

- 👑 **Admin**: Volledige toegang
- 👤 **Viewer**: Alleen-lezen

**Status:**

- ✅ **Actief**: Kan inloggen
- ❌ **Inactief**: Geblokkeerd

### Voorbeeld

```yaml
Gebruikersnaam: j.devries
Email: jan.devries@knahillegom.nl
Wachtwoord: Kna!Theater2026
Rol: Viewer
Status: Actief
```

### Na Aanmaken

De nieuwe gebruiker kan direct inloggen met:

- Gebruikersnaam: `j.devries`
- Wachtwoord: Wat je hebt ingesteld

!!! note "Eerste Login"
    Adviseer de gebruiker om direct het wachtwoord te wijzigen.

## ✏️ Gebruiker Bewerken

### Gegevens Wijzigen

1. Klik op **✏️ Bewerken** bij gebruiker
2. Wijzig velden
3. Klik **Opslaan**

**Wijzigbare velden:**

- Gebruikersnaam
- Email adres
- Rol (Admin ↔ Viewer)
- Status (Actief ↔ Inactief)
- Wachtwoord (optioneel)

### Wachtwoord Resetten

**Optie 1: Als Admin:**

1. Open gebruiker bewerken
2. Vul nieuw wachtwoord in bij "Nieuw wachtwoord"
3. Herhaal wachtwoord ter bevestiging
4. Klik **Opslaan**
5. Informeer gebruiker over nieuwe wachtwoord

**Optie 2: Via Email:**

1. Gebruiker gaat naar login pagina
2. Klikt "Wachtwoord vergeten"
3. Voert email adres in
4. Ontvangt reset link
5. Stelt nieuw wachtwoord in

!!! tip "Tijdelijk Wachtwoord"
    Geef een tijdelijk wachtwoord en vraag gebruiker
    om deze bij eerste login te wijzigen.

### Rol Wijzigen

**Van Viewer naar Admin:**

1. Bewerk gebruiker
2. Selecteer rol: **Admin**
3. Klik **Opslaan**
4. Informeer gebruiker over nieuwe rechten

**Van Admin naar Viewer:**

1. Bewerk gebruiker
2. Selecteer rol: **Viewer**
3. Klik **Opslaan**

!!! warning "Admin Downgraden"
    Je kunt jezelf niet downgraden van admin naar viewer.
    Zorg dat er altijd minimaal één admin account is.

### Gebruiker Deactiveren

In plaats van verwijderen kun je een gebruiker deactiveren:

1. Bewerk gebruiker
2. Zet status op **Inactief**
3. Klik **Opslaan**

**Effect:**

- Account blijft bestaan
- Kan niet inloggen
- Data blijft bewaard
- Kan later gereactiveerd worden

**Gebruik voor:**

- Tijdelijk geblokkeerde gebruikers
- Oud-bestuursleden die niet actief zijn
- Bij verdachte activiteit

## 🗑️ Gebruiker Verwijderen

### Permanent Verwijderen

!!! danger "Onomkeerbaar"
    Verwijderen is permanent en kan niet ongedaan worden!

**Stappen:**

1. Klik **🗑️ Verwijderen** bij gebruiker
2. Bevestig verwijdering
3. Account wordt definitief verwijderd

**Wat wordt verwijderd:**

- Account gegevens
- Login geschiedenis
- Voorkeuren
- Sessies

**Wat blijft bewaard:**

- Data uploads (gekoppeld aan "systeem")
- Audit log entries

### Wanneer Verwijderen?

Verwijder alleen bij:

- ✅ Duplicate accounts
- ✅ Test accounts
- ✅ Op eigen verzoek
- ❌ **Niet** bij tijdelijk blokkeren → Gebruik deactiveren

### Veiligheidsmaatregelen

Je **kunt niet** verwijderen:

- Je eigen admin account
- De laatste admin (moet altijd ≥1 admin zijn)

## 🪪 Gebruiker Profiel

Gebruikers kunnen hun eigen profiel bewerken:

### Toegang

1. Klik op gebruikersnaam rechtsboven
2. Selecteer **Profiel**

### Bewerkbare Velden

**Voor alle gebruikers:**

- Email adres wijzigen
- Wachtwoord wijzigen
- Notificatie voorkeuren
- Taalvoorkeur

**Niet bewerkbaar:**

- Gebruikersnaam (alleen door admin)
- Rol (alleen door admin)

### Wachtwoord Wijzigen

1. Ga naar **Profiel** → **Beveiliging**
2. Voer **huidig wachtwoord** in
3. Voer **nieuw wachtwoord** in (2x)
4. Klik **Wachtwoord Wijzigen**

**Vereisten nieuw wachtwoord:**

- Minimaal 8 karakters
- Niet hetzelfde als vorige 5 wachtwoorden
- Niet gelijk aan gebruikersnaam
- Voldoet aan sterkte-eisen

## 🔑 Sessie Beheer

### Actieve Sessies

Bekijk waar gebruiker is ingelogd:

1. Ga naar **Profiel** → **Sessies**
2. Zie lijst van actieve sessies

**Per sessie zie je:**

- 💻 **Apparaat**: Browser en OS
- 🌍 **Locatie**: IP adres en land
- 🕐 **Laatst actief**: Wanneer laatste activiteit
- 📱 **Type**: Desktop / Mobiel / Tablet

### Sessie Beëindigen

**Andere sessies:**

- Klik **Beëindigen** bij specifieke sessie
- Of klik **Beëindig Alle Andere**

**Eigen sessie:**

- Klik **Uitloggen**

!!! tip "Gebruik bij Beveiliging"
    Als je verdachte activiteit ziet:
    1. Beëindig alle andere sessies
    2. Wijzig wachtwoord
    3. Controleer audit log

## 🕒 Login Geschiedenis

### Bekijken

Toegang via **Profiel** → **Login Geschiedenis**

**Informatie per login:**

- ✅/❌ Succesvol of mislukt
- 🕐 Datum en tijd
- 💻 Apparaat en browser
- 🌍 IP adres
- 📍 Locatie (geschat)

### Filteren

Filter login geschiedenis:

- Laatste week / maand / jaar
- Alleen succesvolle logins
- Alleen mislukte logins
- Specifiek IP adres

### Verdachte Activiteit

Let op:

- ⚠️ Meerdere mislukte logins
- ⚠️ Logins van onbekende locaties
- ⚠️ Logins op vreemde tijden
- ⚠️ Meerdere gelijktijdige sessies

Bij verdacht gedrag:

1. Wijzig onmiddellijk wachtwoord
2. Beëindig alle sessies
3. Schakel 2FA in
4. Informeer andere admins

## 🛡️ Beveiliging

### Two-Factor Authentication (2FA)

Extra beveiligingslaag voor admin accounts:

**Activeren:**

1. **Profiel** → **Beveiliging** → **2FA**
2. Scan QR code met authenticator app
   - Google Authenticator
   - Authy
   - Microsoft Authenticator
3. Voer verificatiecode in
4. Sla backup codes op

**Gebruik:**

- Bij login: normaal wachtwoord + 6-cijferige code
- Code wijzigt elke 30 seconden
- Backup codes voor noodgevallen

!!! warning "Backup Codes Bewaren"
    Bewaar backup codes op veilige plek!
    Bij verlies authenticator app kun je anders niet meer inloggen.

**Deactiveren:**

1. **Profiel** → **Beveiliging** → **2FA**
2. Voer huidige code in
3. Klik **2FA Uitschakelen**

### Wachtwoord Beleid

Admins kunnen wachtwoord eisen instellen:

**Instellingen** → **Beveiliging** → **Wachtwoord Beleid**

| Instelling | Standaard | Aanbevolen |
| ---------- | --------- | ---------- |
| Min. lengte | 8 | 12 |
| Hoofdletters verplicht | Ja | Ja |
| Cijfers verplicht | Ja | Ja |
| Speciale tekens | Nee | Ja |
| Max. leeftijd | Geen | 90 dagen |
| Hergebruik voorkomen | 3 | 5 |

### IP Whitelist

Beperk toegang tot specifieke IP adressen:

**Instellingen** → **Beveiliging** → **IP Whitelist**

1. Klik **IP Toevoegen**
2. Voer IP adres of range in
   - Enkel: `192.168.1.100`
   - Range: `192.168.1.0/24`
3. Geef beschrijving (bijv. "Kantoor")
4. Klik **Toevoegen**

!!! danger "Test Voorzichtig"
    Test eerst met één IP voordat je whitelist activeert!
    Je kunt jezelf buitensluiten.

## 🧾 Audit Log

### Gebruiker Activiteit

Bekijk wat gebruiker heeft gedaan:

1. Ga naar **Gebruikers**
2. Klik op gebruikersnaam
3. Tab **Activiteit**

**Gelogde acties:**

- Data uploads
- Wijzigingen aan data
- Gebruiker aangemaakt/bewerkt
- Login/logout
- Downloads

**Per actie:**

- 👤 Wat (beschrijving)
- 🕐 Wanneer (datum/tijd)
- 💻 Waar (IP adres)
- 📄 Details (wat precies gewijzigd)

### Export

Exporteer activiteit log:

1. Filter op periode/type
2. Klik **Export naar CSV**
3. Open in Excel voor analyse

## 🗂️ Bulk Acties

### Meerdere Gebruikers

Voor veel gebruikers tegelijk:

**Selecteren:**

- Vink checkboxes aan bij gebruikers
- Of klik "Selecteer allen"

**Acties:**

- **Deactiveren**: Alle geselecteerde deactiveren
- **Activeren**: Alle geselecteerde activeren
- **Rol wijzigen**: Allen admin of viewer maken
- **Verwijderen**: Allen verwijderen (met bevestiging)

!!! warning "Wees Voorzichtig"
    Bulk acties zijn krachtig maar riskant.
    Controleer selectie goed voor je bevestigt!

### Import van CSV

Veel gebruikers tegelijk aanmaken:

1. Download CSV template
2. Vul gegevens in:

   ```csv
   username,email,role,password
   j.devries,jan@email.nl,viewer,TempPass123!
   p.janssen,piet@email.nl,admin,AdminPass456!
   ```

3. Upload CSV via **Importeer Gebruikers**
4. Controleer preview
5. Bevestig import

## 📐 Best Practices

### Gebruikersnamen

!!! tip "Consistentie"
    - Gebruik vast patroon (bijv. `v.achternaam`)
    - Geen spaties
    - Geen hoofdletters (voor  eenvoud)
    - Max 30 karakters

### Wachtwoorden

**Voor Admins:**

- Minimaal 16 karakters
- Combinatie letters/cijfers/symbolen
- Uniek (niet hergebruiken)
- 2FA verplicht

**Voor Viewers:**

- Minimaal 12 karakters
- Duidelijke instructies geven
- Verplicht wijzigen bij eerste login

### Rollen

**Admin toekennen alleen aan:**

- Hoofdbestuur
- Webmaster
- IT verantwoordelijke
- Max 3-5 personen

**Viewer toekennen aan:**

- Bestuursleden
- Actieve leden
- Vrijwilligers
- Oud-leden (op verzoek)

### Periodieke Controle

**Maandelijks:**

- Review gebruikerslijst
- Deactiveer inactieve accounts (>90 dagen)
- Check voor verdachte logins

**Jaarlijks:**

- Audit alle admin accounts
- Verwijder oud-bestuursleden
- Update email adressen
- Reset alle wachtwoorden

## 🚑 Problemen Oplossen

### "Gebruiker kan niet inloggen"

**Controleer:**

1. ✅ Account is actief
2. ✅ Wachtwoord correct (let op caps lock)
3. ✅ Email geverifieerd
4. ✅ Geen IP blokkering
5. ✅ Browser cookies toegestaan

**Oplossing:**

- Reset wachtwoord
- Controleer spam folder voor emails
- Test in incognito modus

### "Admin kan zichzelf niet bewerken"

**Normale beperking:**

- Je kunt je eigen rol niet verwijderen
- Je kunt je eigen account niet verwijderen
- Ander admin moet dit doen

### "Email al in gebruik"

**Oorzaak:**

- Email bestaat al in systeem

**Oplossing:**

- Gebruik ander email adres
- Of verwijder/wijzig bestaand account

## ➡️ Volgende Stappen

- [Leer over onderhoud](maintenance.md)
- [Terug naar dashboard](dashboard.md)
- [Data uploaden](data-upload.md)
