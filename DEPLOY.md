# 🚀 Guida al Deploy in Produzione - FIXIT

Guida completa per il deploy di FIXIT su **AWS Lightsail** (Ubuntu/Debian) con **Nginx** come reverse proxy e **Gunicorn** come server WSGI.

> **Architettura**: Internet → Nginx (:80) → Gunicorn (:8000 locale) → Flask app

Nginx gestisce le connessioni TCP (bot, scanner, richieste lente) e passa a Gunicorn solo richieste HTTP valide, eliminando i WORKER TIMEOUT da connessioni fantasma.

---

## 📋 Indice

1. [Prerequisiti](#prerequisiti)
2. [Setup del Server AWS Lightsail](#setup-del-server-aws-lightsail)
3. [Installazione dell'Applicazione](#installazione-dellapplicazione)
4. [Configurazione Gunicorn (WSGI)](#configurazione-gunicorn-wsgi)
5. [Configurazione Nginx (Reverse Proxy)](#configurazione-nginx-reverse-proxy)
6. [Servizio Systemd (Avvio Automatico)](#servizio-systemd-avvio-automatico)
7. [Cron per Monitoraggio e Manutenzione](#cron-per-monitoraggio-e-manutenzione)
8. [Comandi Utili per la Gestione](#comandi-utili-per-la-gestione)
9. [Sviluppo Locale su Windows](#sviluppo-locale-su-windows)
10. [Troubleshooting](#troubleshooting)
11. [Upgrade Futuro a HTTPS](#upgrade-futuro-a-https)

---

## Prerequisiti

### Sul server AWS Lightsail
- Istanza Ubuntu 22.04 LTS (o Debian)
- Python 3.8+ installato
- Porte **22** (SSH) e **80** (HTTP) aperte nel firewall Lightsail

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
sudo apt install python3 python3-pip python3-venv nginx -y
```

### 3. Configura il firewall Lightsail

Dalla console AWS Lightsail:
1. Vai alla tua istanza → **Networking**
2. In **Firewall**, configura le seguenti regole:

| Protocollo | Porta | Note |
|---|---|---|
| SSH | **22** | Accesso remoto |
| HTTP | **80** | Nginx (accesso pubblico) |

> **Importante**: la porta 8000 **NON** deve essere aperta. Gunicorn ascolta solo su `127.0.0.1:8000` (localhost), accessibile solo da Nginx.

---

## Installazione dell'Applicazione

### 1. Crea la directory base del progetto

```bash
sudo mkdir -p /opt/fixit
cd /opt/fixit
```

### 2. Clona o copia il progetto

```bash
git clone <URL-DEL-TUO-REPO> FIXIT
cd FIXIT
```

Oppure copia i file con `scp`:

```bash
# Dal PC Windows (PowerShell):
scp -r .\* ubuntu@<IP-SERVER>:/opt/fixit/FIXIT/
```

### 3. Crea l'ambiente virtuale e installa le dipendenze

> **Nota**: il venv viene creato in `/opt/fixit/venv` (fuori dalla repo), così rimane separato dal codice e non viene sovrascritto da `git pull`.

```bash
cd /opt/fixit
python3 -m venv venv
source /opt/fixit/venv/bin/activate
cd FIXIT
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
ENABLE_PROXY_FIX=False
MAIL_SERVER=mail.dk.dfds.root
MAIL_PORT=25
MAIL_USE_TLS=False
MAIL_DEFAULT_SENDER=FIXIT@dfds.com
MAIL_TIMEOUT=5
TICKET_NOTIFICATION_EMAIL=denitro@dfds.com
```

### 5. Crea le directory necessarie

```bash
mkdir -p static/uploads
mkdir -p instance
```

### 6. Test rapido — verifica che l'app parta

```bash
source /opt/fixit/venv/bin/activate
cd /opt/fixit/FIXIT
python wsgi.py
```

Se funziona (nessun errore), interrompi con `Ctrl+C`.

---

## Configurazione Gunicorn (WSGI)

### Cos'è Gunicorn?

Gunicorn (Green Unicorn) è un server WSGI HTTP per applicazioni Python. A differenza del server di sviluppo Flask, è progettato per la produzione: gestisce più richieste contemporaneamente, è stabile e affidabile.

### Avvio rapido (test)

```bash
cd /opt/fixit/FIXIT
source /opt/fixit/venv/bin/activate
gunicorn wsgi:app -b 127.0.0.1:8000 -w 2
```

> **Nota**: Gunicorn ascolta su `127.0.0.1:8000` (solo localhost). Non è accessibile dall'esterno — Nginx farà da gateway.

### Parametri consigliati

| Parametro | Valore | Descrizione |
|-----------|--------|-------------|
| `-b 127.0.0.1:8000` | Bind address | Ascolta **solo** su localhost, protetto da Nginx |
| `-w 2` | Workers | 2 worker — Nginx gestisce le connessioni lente, SQLite regge |
| `--timeout 120` | Timeout | Secondi prima di terminare un worker lento |
| `--access-logfile -` | Log accessi | Stampa log su stdout (catturato da systemd) |
| `--error-logfile -` | Log errori | Stampa errori su stdout |

### Comando completo consigliato per la produzione

```bash
gunicorn wsgi:app \
    --bind 127.0.0.1:8000 \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

> Con Nginx davanti è sicuro usare `--workers 2` anche con SQLite. Se in futuro passi a PostgreSQL/MySQL puoi aumentare i worker.

---

## Configurazione Nginx (Reverse Proxy)

### Perché Nginx?

Nginx gestisce le connessioni TCP in ingresso e protegge Gunicorn da:
- **Bot e scanner** che aprono connessioni senza inviare dati
- **Connessioni lente** che causavano WORKER TIMEOUT
- **Richieste malformate** (HTTPS su porta HTTP, ecc.)
- Serve i **file statici** direttamente (più veloce di Flask)

### 1. Crea la configurazione Nginx

```bash
sudo nano /etc/nginx/sites-available/fixit
```

Incolla il seguente contenuto:

```nginx
server {
    listen 80;
    server_name _;

    # Dimensione massima upload (allineata a Flask MAX_CONTENT_LENGTH)
    client_max_body_size 16M;

    # Timeout per connessioni lente/bot
    proxy_connect_timeout 10s;
    proxy_read_timeout 120s;
    proxy_send_timeout 120s;

    # File statici serviti direttamente da Nginx (più veloce)
    location /static/ {
        alias /opt/fixit/FIXIT/static/;
        expires 7d;
        access_log off;
    }

    # Tutto il resto va a Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Attiva il sito e rimuovi il default

```bash
# Attiva la configurazione FIXIT
sudo ln -s /etc/nginx/sites-available/fixit /etc/nginx/sites-enabled/

# Rimuovi il sito default di Nginx
sudo rm -f /etc/nginx/sites-enabled/default

# Verifica che la configurazione sia corretta
sudo nginx -t

# Riavvia Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### 3. Verifica

```bash
# Nginx attivo?
sudo systemctl status nginx

# Test locale via Nginx → Gunicorn
curl -s -o /dev/null -w "%{http_code}" http://localhost
# → deve restituire 200
```

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
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/fixit/FIXIT
Environment="PATH=/opt/fixit/venv/bin"
ExecStart=/opt/fixit/venv/bin/gunicorn wsgi:app \
    --bind 127.0.0.1:8000 \
    --workers 2 \
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
# Controlla lo stato di entrambi i servizi
sudo systemctl status fixit
sudo systemctl status nginx

# Controlla i log
sudo journalctl -u fixit -f

# Testa la catena completa (Nginx → Gunicorn → Flask)
curl http://localhost
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
# Health check per FIXIT - riavvia se non risponde (testa via Nginx)

if ! curl -sf http://localhost > /dev/null 2>&1; then
    echo "$(date) - FIXIT non risponde, riavvio in corso..." >> /opt/fixit/fixit_monitor.log
    sudo systemctl restart fixit
    sudo systemctl restart nginx
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

### Gestione dei servizi

```bash
# Stato
sudo systemctl status fixit
sudo systemctl status nginx

# Avvia / Ferma / Riavvia FIXIT
sudo systemctl start fixit
sudo systemctl stop fixit
sudo systemctl restart fixit

# Avvia / Ferma / Riavvia Nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx

# Log Gunicorn/Flask in tempo reale
sudo journalctl -u fixit -f

# Log Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Log delle ultime 100 righe di FIXIT
sudo journalctl -u fixit -n 100

# Log di oggi
sudo journalctl -u fixit --since today
```

### Aggiornamento dell'applicazione

```bash
# 1. Vai nella cartella del progetto
cd /opt/fixit/FIXIT

# 2. Aggiorna il codice
git pull --ff-only origin main

# 3. Attiva il venv e aggiorna le dipendenze
source /opt/fixit/venv/bin/activate
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
- In locale non serve Nginx — il server Flask di sviluppo è sufficiente.

---

## Troubleshooting

### L'app non si avvia

```bash
# Controlla i log di errore di Gunicorn/Flask
sudo journalctl -u fixit -n 50

# Controlla i log di Nginx
sudo tail -20 /var/log/nginx/error.log

# Verifica che il virtual environment sia corretto
/opt/fixit/venv/bin/python -c "import flask; print(flask.__version__)"

# Testa Gunicorn manualmente
cd /opt/fixit/FIXIT
source /opt/fixit/venv/bin/activate
gunicorn wsgi:app -b 127.0.0.1:8000
```

### Nginx restituisce 502 Bad Gateway

Gunicorn non è in esecuzione o non risponde:

```bash
# Verifica che Gunicorn stia girando
sudo systemctl status fixit

# Verifica che la porta 8000 sia in ascolto
sudo ss -tlnp | grep 8000

# Riavvia Gunicorn
sudo systemctl restart fixit
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
# Assicurati che l'utente ubuntu possieda tutta la directory /opt/fixit
sudo chown -R ubuntu:ubuntu /opt/fixit
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

### Nginx — verifica configurazione

```bash
# Testa la configurazione senza riavviare
sudo nginx -t

# Ricarica senza downtime
sudo systemctl reload nginx
```

---

## Upgrade Futuro a HTTPS

Con Nginx già configurato, aggiungere HTTPS è semplice:

### Opzione 1: Let's Encrypt (consigliata — gratuito)

Prerequisito: avere un **dominio** puntato all'IP del server.

```bash
# 1. Installa certbot
sudo apt install certbot python3-certbot-nginx -y

# 2. Aggiorna server_name in Nginx
sudo nano /etc/nginx/sites-available/fixit
# Cambia: server_name _; → server_name tuodominio.com;

# 3. Ricarica Nginx
sudo systemctl reload nginx

# 4. Ottieni certificato SSL gratuito (automatico)
sudo certbot --nginx -d tuodominio.com

# 5. Aggiorna .env
# SESSION_COOKIE_SECURE=True

# 6. Riavvia Flask
sudo systemctl restart fixit
```

Certbot configura automaticamente Nginx per HTTPS e imposta il rinnovo automatico del certificato.

### Opzione 2: AWS Lightsail Load Balancer

Lightsail offre un load balancer integrato con certificato SSL gratuito. Questa è l'opzione più semplice se hai un dominio associato.

### Dopo aver attivato HTTPS

Aggiorna in `.env`:
```env
SESSION_COOKIE_SECURE=True
```

E nel firewall Lightsail aggiungi la porta **443** (HTTPS).

---

**Versione guida**: 1.1  
**Data**: Marzo 2026  
**Compatibile con**: FIXIT 1.0.0 su AWS Lightsail (Ubuntu 22.04)
