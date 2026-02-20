# Future Improvements - FIXIT

## 🔄 Backup Automatico (Sistema Completo)

### 📋 Descrizione
Implementazione di un sistema di backup automatico che:
- ✅ Backup giornalieri locali (Database + uploads)
- ✅ Backup settimanali offsite su Amazon S3
- ✅ Backup completo del progetto settimanalmente
- ✅ Pulizia automatica backup obsoleti (>30 giorni)
- ✅ Interfaccia admin per gestione manuale
- ✅ Task Scheduler Windows per automazione

---

## 📦 File da Creare

### 1. `config.py` - Configurazione centralizzata
```python
import os
from dotenv import load_dotenv

load_dotenv()

# AWS S3 Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET = os.getenv('AWS_S3_BUCKET', 'fixit-backups')
AWS_S3_REGION = os.getenv('AWS_S3_REGION', 'eu-west-1')

# Backup Configuration
BACKUP_LOCAL_DIR = os.getenv('BACKUP_LOCAL_DIR', 'backups')
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))

# Ensure backup directory exists
os.makedirs(BACKUP_LOCAL_DIR, exist_ok=True)
```

### 2. `backup_manager.py` - Core della soluzione
Modulo che gestisce:
- Creazione backup giornalieri (DB + uploads)
- Creazione backup settimanali (progetto completo)
- Upload automatico su S3
- Pulizia backup obsoleti
- Ripristino da backup
- Logging completo

**Funzionalità principali:**
- `create_daily_backup()` - Backup compresso del database e uploads
- `create_weekly_backup()` - Backup completo del progetto (esclude cache/venv)
- `upload_to_s3()` - Upload backup su bucket S3
- `cleanup_old_backups()` - Rimozione automatica backup >30 giorni
- `restore_from_backup()` - Ripristino da backup locale
- `list_backups()` - Elenco backup disponibili

### 3. `scheduler.py` - Automazione task
Script standalone che:
- Pianifica backup giornaliero alle 02:00 AM
- Pianifica backup settimanale domenica 03:00 AM
- Usa libreria `schedule` per gestione task
- Loop infinito con log su file

**Avvio:** `python scheduler.py`

### 4. `.env` - Variabili di ambiente
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=fixit-backups
AWS_S3_REGION=eu-west-1
BACKUP_LOCAL_DIR=backups
BACKUP_RETENTION_DAYS=30
```

### 5. `install_scheduler.bat` - Task Scheduler Windows
Script batch per:
- Creare task pianificato per scheduler.py
- Automatizzare esecuzione backup
- Configurazione per Windows VM

### 6. `templates/backups.html` - Interfaccia di gestione
Pagina admin (superuser-only) con:
- Bottoni azioni rapide (backup manuale, cleanup)
- Lista backup giornalieri con dimensioni e date
- Lista backup settimanali con stato S3
- Informazioni su frequenza e retention

---

## 🔧 Modifiche a File Esistenti

### `app.py`
Aggiungere:
1. Import: `from backup_manager import BackupManager`
2. Nuova route: `@app.route('/admin/backups', methods=['GET', 'POST'])`
   - GET: mostra lista backup (daily + weekly)
   - POST: azioni (create_daily, create_weekly, cleanup)
   - Accesso: solo superuser

### `requirements.txt`
Aggiungere:
```
boto3==1.26.137
python-dotenv==1.0.0
schedule==1.2.0
```

### `templates/base.html`
Aggiungere link navbar:
```html
{% if session.get('is_superuser') %}
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('manage_backups') }}">
        <i class="bi bi-cloud-check me-1"></i>Backup
    </a>
</li>
{% endif %}
```

---

## 🚀 Step-by-Step Implementation

### Fase 1: Preparazione
```bash
# 1. Installa dipendenze
pip install boto3 python-dotenv schedule

# 2. Crea file .env nella root del progetto
# Compila con credenziali AWS

# 3. Crea cartella backups
mkdir backups
```

### Fase 2: Setup AWS S3
1. Vai a AWS Console → IAM
2. Crea nuovo utente con permessi S3
3. Genera Access Key ID e Secret Access Key
4. Copia credenziali in `.env`
5. Crea bucket S3 con nome `fixit-backups`

### Fase 3: Deploy codice
1. Crea file `config.py`
2. Crea file `backup_manager.py`
3. Crea file `scheduler.py`
4. Aggiorna `app.py` con nuova route
5. Crea `templates/backups.html`
6. Aggiungi link a `templates/base.html`
7. Aggiorna `requirements.txt`

### Fase 4: Test locale
```python
# Test backup manuale
python -c "from backup_manager import BackupManager; BackupManager().create_daily_backup()"

# Test scheduler (5 minuti di prova)
python scheduler.py  # Ctrl+C per fermare
```

### Fase 5: Setup Windows Task Scheduler (Produzione)
```powershell
# Esegui come amministratore
.\install_scheduler.bat

# Verifica task creato
Get-ScheduledTask -TaskName "FIXIT_Daily_Backup"

# Visualizza log backup
Get-Content backups\backup.log -Tail 20
```

---

## 📊 Struttura Backup

### Backup Giornaliero (`backup_daily_20260219_020000.zip`)
```
✓ tickets.db              (database SQLite)
✓ static/uploads/*        (immagini e file caricati)
```
**Peso:** ~50-200 MB
**Conservati:** 30 giorni (localmente)

### Backup Settimanale (`backup_weekly_20260216_030000.zip`)
```
✓ app.py
✓ config.py
✓ backup_manager.py
✓ scheduler.py
✓ requirements.txt
✓ templates/
✓ static/
✓ tickets.db
├ (esclusi: __pycache__, .git, venv, instance)
```
**Peso:** ~2-5 MB
**Posizione:** S3 + Locale
**Conservati:** 30 giorni

---

## 📍 Ubicazione Backup

```
FIXIT/
├── backups/                              # Cartella backup locale
│   ├── backup_daily_20260219_020000.zip
│   ├── backup_daily_20260218_020000.zip
│   ├── backup_weekly_20260216_030000.zip
│   └── backup.log                        # Log di tutti i backup
├── config.py                             # ✨ NUOVO
├── backup_manager.py                     # ✨ NUOVO
├── scheduler.py                          # ✨ NUOVO
├── install_scheduler.bat                 # ✨ NUOVO
└── ...

S3 (fixit-backups bucket):
└── fixit-backups/
    ├── weekly/
    │   └── backup_weekly_20260216_030000.zip
    ├── daily/                            # (opzionale)
    │   └── backup_daily_20260219_020000.zip
```

---

## 🔐 Variabili Ambiente (.env)

```env
# AWS S3 Credentials (da AWS IAM)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# S3 Configuration
AWS_S3_BUCKET=fixit-backups
AWS_S3_REGION=eu-west-1

# Backup Settings
BACKUP_LOCAL_DIR=backups
BACKUP_RETENTION_DAYS=30
```

⚠️ **IMPORTANTE**: Non committare `.env` in git! Aggiungere a `.gitignore`:
```
.env
backups/
__pycache__/
*.pyc
instance/
```

---

## ⏰ Schedule Automatico

| Evento | Giorno/Ora | Cosa | Dove |
|--------|-----------|------|------|
| **Daily Backup** | Ogni giorno 02:00 AM | DB + uploads | `./backups/` locale |
| **Weekly Backup** | Domenica 03:00 AM | Progetto intero | S3 + locale |
| **Auto Cleanup** | Dopo ogni daily | Rimuove backup >30gg | Locale |

---

## 📋 Log e Monitoraggio

### File log: `backups/backup.log`

```
2026-02-19 02:00:15 - INFO - Inizio creazione backup giornaliero: backup_daily_20260219_020000.zip
2026-02-19 02:00:16 - INFO - Database aggiunto al backup
2026-02-19 02:00:17 - INFO - Cartella uploads aggiunta al backup
2026-02-19 02:00:18 - INFO - ✅ Backup giornaliero creato: backup_daily_20260219_020000.zip (145.32 MB)
2026-02-19 02:00:19 - INFO - ✅ Pulizia completata: 0 backup rimossi
```

---

## 🎯 Vantaggi della Soluzione

✅ **Automatizzazione**: Nessun intervento manuale richiesto
✅ **Ridondanza**: Backup locali + Cloud offsite
✅ **Sicurezza**: Database + immagini protetti
✅ **Compliance**: Log tracciabili di tutti i backup
✅ **Facilità ripristino**: Uno-click restore da UI admin
✅ **Cost-effective**: S3 storage economico
✅ **Scalabilità**: Suporta file illimitati
✅ **Monitoring**: Dashboard admin in tempo reale

---

## ⚙️ Configurazione Avanzata

### Aumentare retention period
```env
BACKUP_RETENTION_DAYS=90  # Mantieni 3 mesi invece di 1
```

### Backup quotidiani su S3 (opzionale)
Modificare `run_daily_backup()` in `scheduler.py`:
```python
def run_daily_backup():
    manager = BackupManager()
    backup_path = manager.create_daily_backup()
    manager.upload_to_s3(backup_path, 'daily')  # Aggiungi questa riga
    manager.cleanup_old_backups()
    return backup_path
```

### Backup multi-region S3
Abilitare replicazione S3 per disaster recovery

---

## 🐛 Troubleshooting

### "AWS credentials not found"
→ Verifica file `.env` esista e abbia valori corretti

### "Permission denied on S3"
→ Controlla permessi IAM utente

### "Network timeout"
→ Verifica connessione internet e credenziali AWS

### "BackupManager import error"
→ Verifica `config.py` sia nella cartella root

---

## 📝 Prossimi Step (Futuro)

- [ ] Notifiche email su backup falliti
- [ ] Dashboard metriche backup (tempi, dimensioni)
- [ ] Backup incrementali per risparmiare storage
- [ ] Compressione multi-parte per file grandi
- [ ] Encryption backup su S3
- [ ] API ripristino remoto
- [ ] Versioning backup automatico

---

**Versione**: 1.0  
**Data**: Febbraio 2026  
**Status**: 🟨 Da Implementare
