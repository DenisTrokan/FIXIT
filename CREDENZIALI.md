# 🔐 Credenziali di Accesso - FIXIT

## Utenti Amministratori

### Utente Admin Principale
- **Username**: `admin`
- **Password**: `admin123`
- **Ruolo**: Amministratore principale del sistema

### Utenti di Test
Creati con lo script `seed_data.py`:

1. **Mario Rossi**
   - Username: `mario.rossi`
   - Password: `password123`

2. **Luca Bianchi**
   - Username: `luca.bianchi`
   - Password: `password123`

3. **Giulia Verdi**
   - Username: `giulia.verdi`
   - Password: `password123`

---

## 🛠️ Gestione Utenti

### Per aggiungere/eliminare utenti

Usa lo script interattivo:
```bash
python manage_users.py
```

### Funzionalità disponibili:
- ✅ Lista tutti gli utenti con statistiche
- ➕ Aggiungi nuovo utente
- 🗑️ Elimina utente esistente
- 🔑 Cambia password utente

---

## 📊 Dati di Test

Il database è stato popolato con:
- **4 utenti totali** (1 admin + 3 test)
- **10 ticket di esempio**:
  - 5 Interventi Mezzi
  - 5 Interventi Tecnici
  - Stati variabili (Nuovo, In Lavorazione, Risolto)
  - Assegnazioni casuali agli utenti

---

## ⚠️ Nota Sicurezza

**IMPORTANTE**: In produzione:
1. Cambia la password dell'admin predefinito
2. Elimina gli utenti di test
3. Usa password sicure per tutti gli account
4. Modifica la `SECRET_KEY` in `app.py`

---

**File generato automaticamente** - Gennaio 2026
