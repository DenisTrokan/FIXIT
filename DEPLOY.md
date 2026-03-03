# 🚀 Guida al Deploy in Produzione - FIXIT

Guida completa per il deploy di FIXIT su **AWS Lightsail** (Ubuntu/Debian) con Gunicorn come server WSGI e configurazione per mantenere l'applicazione attiva 24/7.

> **Nota**: Questa guida è per la versione 1.0 con HTTP. HTTPS potrà essere aggiunto in seguito con un reverse proxy (nginx + Let's Encrypt).

---

## 📋 Indice

1. [Prerequisiti](#prerequisiti)
2. [Setup del Server AWS Lightsail](#setup-del-server-aws-lightsail)
3. [Installazione dell'Applicazione](#installazione-dellapplicazione)
4. [Configurazione Gunicorn (WSGI)](#configurazione-gunicorn-wsgi)
5. [Servizio Systemd (Avvio Automatico)](#servizio-systemd-avvio-automatico)
6. [Cron per Monitoraggio e Manutenzione](#cron-per-monitoraggio-e-manutenzione)
7. [Comandi Utili per la Gestione](#comandi-utili-per-la-gestione)
8. [Sviluppo Locale su Windows](#sviluppo-locale-su-windows)
9. [Troubleshooting](#troubleshooting)
10. [Upgrade Futuro a HTTPS](#upgrade-futuro-a-https)

---

## Prerequisiti

### Sul server AWS Lightsail
- Istanza Ubuntu 22.04 LTS (o Debian)
- Python 3.8+ installato
- Porta **8000** (o la porta scelta) aperta nel firewall Lightsail

### Sul PC Windows (sviluppo)
- Python 3.8+
- pip installato
- Git (opzionale ma consigliato)

---

## Setup del Server AWS Lightsail

### 1. Connettiti al server

Usa la console SSH di Lightsail oppure il tuo client SSH:

```bash
ssh ubuntu@<IP-DEL-TUO-SERVER>
```

### 2. Aggiorna il sistema e installa le dipendenze

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv -y
```

### 3. Apri la porta nel firewall Lightsail

Dalla console AWS Lightsail:
1. Vai alla tua istanza → **Networking**
2. In **Firewall**, clicca **Add rule**
3. Aggiungi: **Custom TCP**, porta **8000**
4. Salva

---

## Installazione dell'Applicazione

### 1. Crea un utente dedicato (consigliato)

```bash
sudo useradd -m -s /bin/bash fixit
sudo su - fixit
```

### 2. Clona o copia il progetto

```bash
sudo mkdir -p /opt/fixit
sudo chown fixit:fixit /opt/fixit
cd /opt/fixit
git clone <URL-DEL-TUO-REPO> FIXIT
cd FIXIT
```

Oppure copia i file con `scp`:

```bash
# Dal PC Windows (PowerShell):
scp -r .\* ubuntu@<IP-SERVER>:/opt/fixit/FIXIT/
```

### 3. Crea l'ambiente virtuale e installa le dipendenze

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configura le variabili d'ambiente

```bash
cp .env.example .env
nano .env
```

Modifica `.env` con valori sicuri per la produzione:

```env
SECRET_KEY=<genera-con-python -c "import secrets; print(secrets.token_hex(32))">
FLASK_ENV=production
ADMIN_PASSWORD=<password-sicura>
SESSION_COOKIE_SECURE=False
```

### 5. Crea le directory necessarie

```bash
mkdir -p static/uploads
mkdir -p instance
```

### 6. Test rapido — verifica che l'app parta

```bash
source venv/bin/activate
python wsgi.py
```

Se funziona (nessun errore), interrompi con `Ctrl+C`.

---

## Configurazione Gunicorn (WSGI)

### Cos'è Gunicorn?

Gunicorn (Green Unicorn) è un server WSGI HTTP per applicazioni Python. A differenza del server di sviluppo Flask, è progettato per la produzione: gestisce più richieste contemporaneamente, è stabile e affidabile.

### Avvio rapido

```bash
cd /opt/fixit/FIXIT
source venv/bin/activate
gunicorn wsgi:app -b 0.0.0.0:8000 -w 1
```

L'app sarà raggiungibile su `http://<IP-SERVER>:8000`

### Parametri consigliati

| Parametro | Valore | Descrizione |
|-----------|--------|-------------|
| `-b 0.0.0.0:8000` | Bind address | Ascolta su tutte le interfacce, porta 8000 |
| `-w 1` | Workers | Con SQLite consigliato 1 worker per evitare lock in scrittura |
| `--timeout 120` | Timeout | Secondi prima di terminare un worker lento |
| `--access-logfile -` | Log accessi | Stampa log su stdout (catturato da systemd) |
| `--error-logfile -` | Log errori | Stampa errori su stdout |

### Comando completo consigliato per la produzione

```bash
gunicorn wsgi:app \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

> Nota: con database SQLite è preferibile usare `--workers 1` per stabilità. Se in futuro passi a PostgreSQL/MySQL puoi aumentare i worker.

---

## Servizio Systemd (Avvio Automatico)

Il servizio systemd garantisce che FIXIT:
- **Si avvii automaticamente** al boot del server
- **Si riavvii automaticamente** in caso di crash
- Gestisca i log tramite `journalctl`

### 1. Crea il file di servizio

```bash
sudo nano /etc/systemd/system/fixit.service
```

Incolla il seguente contenuto:

```ini
[Unit]
Description=FIXIT Ticketing System (Gunicorn)
After=network.target

[Service]
User=fixit
Group=fixit
WorkingDirectory=/opt/fixit/FIXIT
Environment="PATH=/opt/fixit/FIXIT/venv/bin"
ExecStart=/opt/fixit/FIXIT/venv/bin/gunicorn wsgi:app \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Attiva e avvia il servizio

```bash
sudo systemctl daemon-reload
sudo systemctl enable fixit          # Avvio automatico al boot
sudo systemctl start fixit           # Avvia ora
sudo systemctl status fixit          # Verifica stato
```

### 3. Verifica che funzioni

```bash
# Controlla lo stato
sudo systemctl status fixit

# Controlla i log
sudo journalctl -u fixit -f

# Testa dall'esterno
curl http://localhost:8000
```

---

## Cron per Monitoraggio e Manutenzione

### 1. Health check — riavvio automatico se l'app non risponde

Crea lo script di health check:

```bash
sudo nano /opt/fixit/check_fixit.sh
```

Contenuto:

```bash
#!/bin/bash
# Health check per FIXIT - riavvia se non risponde

if ! curl -sf http://localhost:8000 > /dev/null 2>&1; then
    echo "$(date) - FIXIT non risponde, riavvio in corso..." >> /opt/fixit/fixit_monitor.log
    sudo systemctl restart fixit
else
    echo "$(date) - FIXIT OK" >> /opt/fixit/fixit_monitor.log
fi
```

Rendi eseguibile:

```bash
sudo chmod +x /opt/fixit/check_fixit.sh
```

### 2. Configura il cron job

```bash
sudo crontab -e
```

Aggiungi queste righe:

```cron
# Health check FIXIT ogni 5 minuti
*/5 * * * * /opt/fixit/check_fixit.sh

# Pulizia log monitor ogni settimana (domenica alle 03:00)
0 3 * * 0 truncate -s 0 /opt/fixit/fixit_monitor.log
```

### 3. Verifica i cron job

```bash
sudo crontab -l
```

---

## Comandi Utili per la Gestione

### Gestione del servizio

```bash
# Stato
sudo systemctl status fixit

# Avvia / Ferma / Riavvia
sudo systemctl start fixit
sudo systemctl stop fixit
sudo systemctl restart fixit

# Log in tempo reale
sudo journalctl -u fixit -f

# Log delle ultime 100 righe
sudo journalctl -u fixit -n 100

# Log di oggi
sudo journalctl -u fixit --since today
```

### Aggiornamento dell'applicazione

```bash
# 1. Vai nella cartella del progetto
cd /opt/fixit/FIXIT

# 2. Aggiorna il codice
git pull origin main

# 3. Attiva il venv e aggiorna le dipendenze
source venv/bin/activate
pip install -r requirements.txt

# 4. Riavvia il servizio
sudo systemctl restart fixit

# 5. Verifica
sudo systemctl status fixit
```

---

## Sviluppo Locale su Windows

Per sviluppare e testare su Windows (prima di fare il deploy su Lightsail):

### Avvio in modalità sviluppo

```powershell
# Crea e attiva il virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Installa le dipendenze
pip install -r requirements.txt

# Avvia l'app in modalità sviluppo
python app.py
```

L'app sarà disponibile su `http://localhost:5000`

### Note importanti

- **Gunicorn non funziona su Windows**. Per lo sviluppo locale usa `python app.py` (server Flask integrato).
- Per testare il WSGI entry point su Windows puoi usare **waitress** come alternativa:

```powershell
pip install waitress
python -c "from waitress import serve; from wsgi import app; serve(app, host='0.0.0.0', port=8000)"
```

- Il file `wsgi.py` funziona sia con Gunicorn (Linux/produzione) sia con Waitress (Windows/test).

---

## Troubleshooting

### L'app non si avvia

```bash
# Controlla i log di errore
sudo journalctl -u fixit -n 50

# Verifica che il virtual environment sia corretto
/opt/fixit/FIXIT/venv/bin/python -c "import flask; print(flask.__version__)"

# Testa manualmente
cd /opt/fixit/FIXIT
source venv/bin/activate
gunicorn wsgi:app -b 0.0.0.0:8000
```

### "Address already in use"

```bash
# Trova il processo che usa la porta
sudo lsof -i :8000
# oppure
sudo ss -tlnp | grep 8000

# Termina il processo
sudo kill <PID>
```

### Permessi negati sui file

```bash
# Assicurati che l'utente fixit possieda tutti i file
sudo chown -R fixit:fixit /opt/fixit/FIXIT
```

### Database locked

```bash
# Riavvia il servizio per rilasciare il lock
sudo systemctl restart fixit
```

### Il cron non funziona

```bash
# Verifica che il cron sia attivo
sudo systemctl status cron

# Controlla il log
cat /opt/fixit/fixit_monitor.log
```

---

## Upgrade Futuro a HTTPS

Per la versione 1.0 l'applicazione funziona con HTTP. Quando sarà necessario aggiungere HTTPS:

### Opzione 1: Nginx come reverse proxy + Let's Encrypt (consigliata)

```bash
# 1. Installa nginx e certbot
sudo apt install nginx certbot python3-certbot-nginx -y

# 2. Configura nginx come reverse proxy
sudo nano /etc/nginx/sites-available/fixit
```

Configurazione nginx:

```nginx
server {
    listen 80;
    server_name tuodominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /opt/fixit/FIXIT/static;
    }
}
```

```bash
# 3. Attiva il sito
sudo ln -s /etc/nginx/sites-available/fixit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 4. Ottieni certificato SSL gratuito
sudo certbot --nginx -d tuodominio.com

# 5. Aggiorna .env
# SESSION_COOKIE_SECURE=True
```

### Opzione 2: AWS Lightsail Load Balancer

Lightsail offre un load balancer integrato con certificato SSL gratuito. Questa è l'opzione più semplice se hai un dominio associato.

Quando attivi HTTPS, ricorda di aggiornare in `.env`:
```env
SESSION_COOKIE_SECURE=True
```

---

**Versione guida**: 1.0  
**Data**: Marzo 2026  
**Compatibile con**: FIXIT 1.0.0 su AWS Lightsail (Ubuntu 22.04)
