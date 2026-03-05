# 📘 User Guide Breve - FIXIT

Questa guida spiega in modo rapido come usare il sito FIXIT per inserire e gestire ticket.

## 1) Accesso al sito

- **Homepage pubblica**: `http://63.179.13.224:8000/`
- **Login admin**: `http://63.179.13.224:8000/admin/login`

---

## 2) Apertura ticket (area pubblica)

Dalla homepage puoi scegliere:

- **Intervento Mezzi**
- **Intervento Tecnico**

### Campi principali

- Nome richiedente
- Descrizione problema
- Eventuali campi specifici (mezzo, priorità, ecc.)
- Foto opzionale (jpg, jpeg, png)

Alla conferma:

- viene creato il ticket con numero progressivo
- il ticket compare in dashboard admin
- viene inviata una mail di notifica automatica (se SMTP configurato)

---

## 3) Dashboard admin

Dopo login, in **Dashboard** puoi:

- vedere tutti i ticket ordinati dal più recente
- cercare per ID, nome o descrizione
- filtrare per stato o assegnazione
- aprire il dettaglio ticket

---

## 4) Dettaglio ticket

Nel dettaglio puoi:

- cambiare stato: **NUOVO → IN_LAVORAZIONE → RISOLTO**
- assegnare il ticket a un operatore
- aggiungere commenti
- (ticket tecnici) aggiornare la priorità
- eliminare ticket (operazione irreversibile)

---

## 5) Gestione utenti (solo superuser)

Nel menu **Utenze** (visibile ai superuser) puoi:

- creare nuovi utenti
- eliminare utenti
- reimpostare password
- assegnare/rimuovere ruolo superuser

---

## 6) Buone pratiche operative

- Inserire descrizioni chiare e complete
- Allegare foto quando utile
- Aggiornare subito stato e assegnazione
- Usare i commenti per tracciare attività e passaggi

---

**Versione guida**: 1.0  
**Data**: Marzo 2026
