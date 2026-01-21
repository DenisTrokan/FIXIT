# FIXIT - Sistema di Ticketing Aziendale

Sistema MVP per la gestione di ticket aziendali con focus su interventi tecnici e manutenzione mezzi.

## 🚀 Caratteristiche

- **Doppio tipo di ticket**: Intervento Mezzi e Intervento Tecnico
- **Interfaccia pubblica** per la creazione di segnalazioni
- **Back-office protetto** per la gestione amministrativa
- **Sistema di priorità e assegnazione** ticket
- **Upload e visualizzazione immagini**
- **Filtri avanzati** per ricerca ticket
- **Tracciamento completo** con timestamp automatici

## 📋 Requisiti

- Python 3.8 o superiore
- pip (Python package manager)

## 🔧 Installazione

### 1. Clona o scarica il progetto

```powershell
cd "c:\Users\denitro\OneDrive - DFDS\Desktop\vsCode\FIXIT"
```

### 2. Crea un ambiente virtuale (opzionale ma consigliato)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Installa le dipendenze

```powershell
pip install -r requirements.txt
```

## 🎯 Avvio dell'Applicazione

### Primo avvio (inizializzazione database)

```powershell
python app.py
```

Al primo avvio, l'applicazione:
- Creerà automaticamente il database SQLite (`tickets.db`)
- Creerà la cartella per gli upload (`static/uploads`)
- Creerà l'utente admin predefinito:
  - **Username**: `admin`
  - **Password**: `admin123`

### Avvii successivi

```powershell
python app.py
```

L'applicazione sarà disponibile all'indirizzo:
- **URL**: http://localhost:5000

## 👥 Accesso

### Area Pubblica
Accessibile a tutti senza autenticazione:
- Homepage: http://localhost:5000
- Form Intervento Mezzi: http://localhost:5000/new/mezzi
- Form Intervento Tecnico: http://localhost:5000/new/tecnico

### Area Admin
Richiede autenticazione:
- Login: http://localhost:5000/admin/login
- Dashboard: http://localhost:5000/admin/dashboard

**Credenziali predefinite**:
- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANTE**: Cambiare la password predefinita in produzione!

## 📁 Struttura del Progetto

```
FIXIT/
│
├── app.py                      # Applicazione Flask principale
├── requirements.txt            # Dipendenze Python
├── README.md                   # Questo file
├── tickets.db                  # Database SQLite (creato al primo avvio)
│
├── templates/                  # Template Jinja2
│   ├── base.html              # Template base
│   ├── index.html             # Homepage pubblica
│   ├── form_mezzi.html        # Form intervento mezzi
│   ├── form_tecnico.html      # Form intervento tecnico
│   ├── login.html             # Login admin
│   ├── dashboard.html         # Dashboard admin
│   └── ticket_detail.html     # Dettaglio ticket
│
└── static/                     # File statici
    └── uploads/               # Immagini caricate (creata automaticamente)
```

## 🎨 Funzionalità

### Area Pubblica

#### 1. Homepage
- Scelta del tipo di segnalazione
- Design pulito e intuitivo

#### 2. Form Intervento Mezzi
- Raccolta dati veicolo
- Selezione categoria anomalia predefinita
- Descrizione dettagliata problema

#### 3. Form Intervento Tecnico
- Informazioni richiedente e reparto
- Selezione priorità (Bassa/Media/Alta)
- Upload foto opzionale

### Area Admin

#### 1. Dashboard
- Visualizzazione tabellare di tutti i ticket
- **Filtri**:
  - Ricerca per keyword (ID, nome, descrizione)
  - Filtro per status
  - Filtro per assegnatario
- Badge colorati per status e priorità
- Indicatore presenza foto

#### 2. Dettaglio Ticket
- Visualizzazione completa informazioni
- **Gestione Status**:
  - Cambio stato (Nuovo → In Lavorazione → Risolto)
  - Timestamp automatici per ogni transizione
- **Assegnazione**:
  - Assegna/riassegna ticket agli admin
- **Eliminazione**:
  - Rimozione permanente ticket e foto associate

## 🗄️ Schema Database

### Tabella `users`
- `id`: Primary Key
- `username`: String (unique)
- `password_hash`: String (hashed)

### Tabella `tickets`
- `id`: Primary Key
- `ticket_type`: MEZZO | TECNICO
- `status`: NUOVO | IN_LAVORAZIONE | RISOLTO
- `created_at`, `started_at`, `closed_at`: Timestamps
- `requester_name`, `description`: Info base
- `image_filename`: Nome file immagine
- `assigned_to_id`: FK verso users

**Campi specifici MEZZO**:
- `vehicle_type`, `vehicle_number`, `mileage_hours`, `anomaly_category`

**Campi specifici TECNICO**:
- `department`, `title`, `priority`

## 🔒 Sicurezza

- Password hashate con Werkzeug
- Sessioni protette con SECRET_KEY
- Validazione file upload (solo jpg, jpeg, png)
- Limite dimensione upload: 16MB
- Decoratore `@login_required` per rotte admin

## 🛠️ Personalizzazione

### Cambiare la porta

Nel file `app.py`, modifica l'ultima riga:

```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Cambia 5000 con la porta desiderata
```

### Gestire gli utenti admin

#### Script di gestione utenti interattivo

Usa lo script `manage_users.py` per gestire gli utenti:

```powershell
python manage_users.py
```

Funzionalità disponibili:
- **Lista utenti**: Visualizza tutti gli utenti con ticket assegnati
- **Aggiungi utente**: Crea un nuovo utente admin
- **Elimina utente**: Rimuove un utente (i ticket assegnati vengono liberati)
- **Cambia password**: Modifica la password di un utente esistente

#### Aggiungere utenti tramite Python

Puoi anche aggiungere utenti direttamente:

```python
from app import app, db, User

with app.app_context():
    new_admin = User(username='nuovo_admin')
    new_admin.set_password('password_sicura')
    db.session.add(new_admin)
    db.session.commit()
```

### Popolare il database con dati di test

Per testare l'applicazione con dati di esempio:

```powershell
python seed_data.py
```

Questo script crea:
- **3 utenti di test**: mario.rossi, luca.bianchi, giulia.verdi (password: password123)
- **10 ticket di esempio**: mix di interventi mezzi e tecnici con vari stati

Lo script è idempotente e può essere eseguito più volte senza creare duplicati.

### Modificare categorie anomalie

Nel file `app.py`, nella funzione `new_mezzi()`, modifica la lista `anomaly_categories`.

## 📝 Note Tecniche

- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy
- **Database**: SQLite (file singolo, facile da gestire)
- **Frontend**: Bootstrap 5 (via CDN)
- **Template Engine**: Jinja2
- **File Storage**: Filesystem locale

## 🐛 Troubleshooting

### Errore "Port already in use"
Un'altra applicazione sta usando la porta 5000. Cambia la porta in `app.py` o termina l'altra applicazione.

### Database locked
Chiudi tutte le connessioni al database e riavvia l'applicazione.

### Immagini non visualizzate
Verifica che la cartella `static/uploads` esista e abbia i permessi corretti.

## 📧 Supporto

Per problemi o domande, contatta il team di sviluppo.

---

**Versione**: 1.0.0  
**Data**: Gennaio 2026  
**Sviluppato con**: Python + Flask + Bootstrap 5
