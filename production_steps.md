# Roadmap prossimi step per andare in produzione (FIXIT)

## Obiettivo
Portare l'app Flask su Lightsail Ubuntu in modo sicuro e ripetibile, mantenendo costi contenuti.

## Stima totale
**Circa 16-26 ore** (PoC -> produzione base affidabile).

---

## Fase 1 - Hardening base server (2-4h)
1. Aggiornamento sistema e pacchetti (`apt update/upgrade`) — **0.5h**
2. Configurazione firewall Lightsail/OS (porte 22, 80, 443) — **0.5h**
3. Utente operativo + permessi cartelle app (`/opt/fixit`) — **0.5h**
4. Verifica logica segreti (`.env` solo su server, non su Git) — **0.5-1h**
5. Rotazione chiavi/credenziali iniziali — **0.5-1h**

## Fase 2 - Deploy applicazione (2-3h)
1. Clone repository in server (`git clone`) — **0.5h**
2. Setup `venv` + `pip install -r requirements.txt` — **0.5h**
3. Inizializzazione DB (`init_db`) e cartelle upload — **0.5h**
4. Smoke test applicativo (login, ticket, upload) — **0.5-1h**

## Fase 3 - Runtime produzione (Gunicorn + systemd) (2-3h)
1. Installazione Gunicorn — **0.5h**
2. Creazione service `systemd` (auto-start, restart on failure) — **1h**
3. Verifica log e restart policy — **0.5h**
4. Test reboot server e ripartenza automatica — **0.5-1h**

## Fase 4 - Reverse proxy + HTTPS (3-4h)
1. Configurazione Nginx reverse proxy — **1-1.5h**
2. Setup dominio/DNS — **0.5-1h**
3. Certificato TLS (Let's Encrypt + auto renew) — **1-1.5h**
4. Verifica headers base sicurezza e redirect HTTP->HTTPS — **0.5h**

## Fase 5 - Backup e restore automatici (3-5h)
1. Script backup `tickets.db` + `static/uploads` — **1-1.5h**
2. Scheduling (cron) giornaliero/settimanale — **0.5-1h**
3. Snapshot Lightsail automatici — **0.5h**
4. Offsite secondario (S3/SharePoint) opzionale ma consigliato — **0.5-1h**
5. Test restore completo su istanza nuova — **0.5-1h**

## Fase 6 - Processo release/rollback (2-3h)
1. Convenzione branch/tag (es. `v0.x.y`) — **0.5h**
2. Script deploy (pull tag + restart service) — **0.5-1h**
3. Script rollback (tag precedente + restore backup se serve) — **0.5-1h**
4. Checklist rilascio pre/post deploy — **0.5h**

## Fase 7 - Monitoraggio minimo (2-4h)
1. Alert uptime (endpoint healthcheck) — **0.5-1h**
2. Alert risorse (CPU/RAM/disk) — **0.5-1h**
3. Alert backup falliti — **0.5-1h**
4. Runbook incidente (chi fa cosa, tempi, escalation) — **0.5-1h**

---

## Frequenze operative consigliate
- Deploy applicativo: **1 volta/settimana** (cambi piccoli)
- Backup DB: **ogni 4h** o almeno **giornaliero**
- Backup upload: **giornaliero**
- Snapshot istanza: **settimanale** (meglio giornaliero se possibile)
- Test restore: **mensile**

---

## Criterio di “go-live” minimo
Vai live quando sono completate almeno:
1. Fase 1
2. Fase 2
3. Fase 3
4. Fase 4
5. Fase 5 (con almeno un restore testato)

---

## Nota per il tuo scenario attuale (PoC)
Se vuoi partire velocemente, puoi fare un **Go-Live Light in 8-12h** completando:
- Fase 1 (ridotta)
- Fase 2
- Fase 3
- Fase 4
- Fase 5 solo con snapshot Lightsail + backup giornaliero DB

Poi completi monitoraggio e processo release nelle 2 settimane successive.
