"""
Script per popolare il database con dati di esempio
Esegui: python seed_data.py
"""

from app import app, db, User, Ticket, Comment
from datetime import datetime, timedelta
import random

def seed_users():
    """Crea 3 utenti di test"""
    print("Creazione utenti di test...")
    
    users_data = [
        {'username': 'mario.rossi', 'password': 'password123'},
        {'username': 'luca.bianchi', 'password': 'password123'},
        {'username': 'giulia.verdi', 'password': 'password123'}
    ]
    
    created_users = []
    for user_data in users_data:
        # Verifica se l'utente esiste già
        existing = User.query.filter_by(username=user_data['username']).first()
        if not existing:
            user = User(username=user_data['username'])
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
            print(f"✓ Creato utente: {user_data['username']}")
        else:
            created_users.append(existing)
            print(f"- Utente già esistente: {user_data['username']}")
    
    db.session.commit()
    return created_users


def seed_tickets(users):
    """Crea 10 ticket di esempio"""
    print("\nCreazione ticket di esempio...")
    
    # Nomi di esempio
    requester_names = [
        "Marco Ferrari", "Anna Russo", "Paolo Colombo", 
        "Silvia Romano", "Davide Marino", "Francesca Ricci",
        "Alessandro Gallo", "Laura Conti", "Roberto Esposito"
    ]
    
    # Dati per ticket MEZZO
    vehicle_types = ["Mafi", "Ralla", "Forklift", "Carrello Elevatore", "Trattore"]
    anomaly_categories = [
        "Livello Olio/Liquidi", "Perdite Liquidi", "Pneumatici", 
        "Carrozzeria", "Spie/Allarmi", "Dispositivi Segnalazione",
        "Freni/Sterzo/Cambio", "Braccio/Spreader", "Rumori Insoliti", 
        "Incidenti/Danni", "Altri Problemi"
    ]
    
    # Dati per ticket TECNICO
    departments = ["IT", "Manutenzione", "Amministrazione", "Logistica", "Produzione"]
    priorities = ["BASSA", "MEDIA", "ALTA"]
    statuses = ["NUOVO", "IN_LAVORAZIONE", "RISOLTO"]
    
    # Commenti di esempio
    sample_comments = [
        "Verificato il sistema: tutto funziona correttamente",
        "Intervento in corso. Parti già ordinate.",
        "Problema risolto. Verifica finale completata.",
        "In attesa di ricambi. Previsto arrivo domani.",
        "Cliente informato. Procediamo con la riparazione.",
        "Diagnostica completata. Rischio basso.",
        "Sostituzione componente eseguita con successo.",
        "Ritardo dovuto alla disponibilità ricambi.",
        "Tutte le verifiche sono state superate."
    ]
    
    tickets_data = [
        # Ticket MEZZO
        {
            'type': 'MEZZO',
            'requester': random.choice(requester_names),
            'vehicle_type': 'Forklift',
            'vehicle_number': 'FL-042',
            'mileage_hours': '1.250 ore',
            'anomaly_category': 'Spie/Allarmi',
            'description': 'Spia motore accesa durante le operazioni di carico. Il mezzo continua a funzionare ma richiede verifica urgente.',
            'status': 'NUOVO'
        },
        {
            'type': 'MEZZO',
            'requester': random.choice(requester_names),
            'vehicle_type': 'Mafi',
            'vehicle_number': 'MF-108',
            'mileage_hours': '3.450 Km',
            'anomaly_category': 'Perdite Liquidi',
            'description': 'Notata perdita di olio idraulico sotto il mezzo. Chiazza evidente nel piazzale di stazionamento.',
            'status': 'IN_LAVORAZIONE',
            'comments': [
                ('mario.rossi', 'Ho controllato il livello dell\'olio. Sotto il minimo.'),
                ('luca.bianchi', 'Identificata perdita dalla guarnizione cilindro. Procedo con la sostituzione.')
            ]
        },
        {
            'type': 'MEZZO',
            'requester': random.choice(requester_names),
            'vehicle_type': 'Ralla',
            'vehicle_number': 'RL-225',
            'mileage_hours': '890 Km',
            'anomaly_category': 'Pneumatici',
            'description': 'Pneumatico anteriore destro con usura eccessiva e possibile foratura lenta.',
            'status': 'RISOLTO',
            'comments': [
                ('giulia.verdi', 'Pneumatico sostituito con uno nuovo di qualità superiore.'),
                ('mario.rossi', 'Verifica completata. Tutto in ordine.'),
                ('admin', 'Ticket chiuso. Cliente soddisfatto.')
            ]
        },
        {
            'type': 'MEZZO',
            'requester': random.choice(requester_names),
            'vehicle_type': 'Carrello Elevatore',
            'vehicle_number': 'CE-017',
            'mileage_hours': '2.100 ore',
            'anomaly_category': 'Freni/Sterzo/Cambio',
            'description': 'Sterzo duro e poco reattivo. Difficoltà nelle manovre in spazi stretti.',
            'status': 'NUOVO'
        },
        {
            'type': 'MEZZO',
            'requester': random.choice(requester_names),
            'vehicle_type': 'Mafi',
            'vehicle_number': 'MF-095',
            'mileage_hours': '5.670 Km',
            'anomaly_category': 'Rumori Insoliti',
            'description': 'Rumore metallico proveniente dal vano motore durante l\'accelerazione.',
            'status': 'IN_LAVORAZIONE',
            'comments': [
                ('luca.bianchi', 'Rumore identificato: cinghia di distribuzione usurata.'),
            ]
        },
        
        # Ticket TECNICO
        {
            'type': 'TECNICO',
            'requester': random.choice(requester_names),
            'department': 'IT',
            'title': 'Stampante ufficio non risponde',
            'priority': 'MEDIA',
            'description': 'La stampante del piano 2 non stampa da questa mattina. Il LED verde lampeggia ma non viene rilevata dalla rete.',
            'status': 'NUOVO'
        },
        {
            'type': 'TECNICO',
            'requester': random.choice(requester_names),
            'department': 'Manutenzione',
            'title': 'Perdita acqua nel locale caldaia',
            'priority': 'ALTA',
            'description': 'Rilevata perdita d\'acqua nel locale caldaia. Necessario intervento immediato per evitare danni maggiori.',
            'status': 'IN_LAVORAZIONE',
            'comments': [
                ('mario.rossi', 'Isolato il tubo interessato. Procedura di drenaggio in corso.'),
                ('giulia.verdi', 'Ricambio ordinato. Disponibile domani mattina.')
            ]
        },
        {
            'type': 'TECNICO',
            'requester': random.choice(requester_names),
            'department': 'Amministrazione',
            'title': 'Installazione software contabilità',
            'priority': 'BASSA',
            'description': 'Richiesta installazione nuovo software di contabilità su 3 postazioni ufficio amministrativo.',
            'status': 'RISOLTO',
            'comments': [
                ('luca.bianchi', 'Download del software completato.'),
                ('admin', 'Installazione completata su tutte e 3 le postazioni. Formazione fornita al personale.'),
                ('giulia.verdi', 'Verificato il corretto funzionamento. Ticket chiuso.')
            ]
        },
        {
            'type': 'TECNICO',
            'requester': random.choice(requester_names),
            'department': 'Logistica',
            'title': 'Sistema RFID non legge badge',
            'priority': 'ALTA',
            'description': 'Il lettore RFID all\'ingresso magazzino non legge i badge degli operatori. Blocco operativo.',
            'status': 'NUOVO'
        },
        {
            'type': 'TECNICO',
            'requester': random.choice(requester_names),
            'department': 'Produzione',
            'title': 'Illuminazione area produzione insufficiente',
            'priority': 'MEDIA',
            'description': 'Alcuni neon nella zona produzione sono bruciati. Necessaria sostituzione per garantire sicurezza.',
            'status': 'IN_LAVORAZIONE',
            'comments': [
                ('mario.rossi', 'Identificati 4 neon fuori servizio nella zona B.'),
                ('luca.bianchi', 'Ordinati i ricambi. Installazione prevista per domani.')
            ]
        }
    ]
    
    created_tickets = []
    base_date = datetime.now()
    
    for i, ticket_data in enumerate(tickets_data):
        # Crea timestamp realistici (ultimi 10 giorni)
        days_ago = 10 - i
        created_at = base_date - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        ticket = Ticket(
            ticket_type=ticket_data['type'],
            requester_name=ticket_data['requester'],
            description=ticket_data['description'],
            status=ticket_data['status'],
            created_at=created_at
        )
        
        # Campi specifici per MEZZO
        if ticket_data['type'] == 'MEZZO':
            ticket.vehicle_type = ticket_data['vehicle_type']
            ticket.vehicle_number = ticket_data['vehicle_number']
            ticket.mileage_hours = ticket_data['mileage_hours']
            ticket.anomaly_category = ticket_data['anomaly_category']
        
        # Campi specifici per TECNICO
        else:
            ticket.department = ticket_data['department']
            ticket.title = ticket_data['title']
            ticket.priority = ticket_data['priority']
        
        # Assegna casualmente alcuni ticket agli utenti
        if random.random() > 0.3:  # 70% di probabilità di essere assegnato
            ticket.assigned_to_id = random.choice(users).id
        
        # Aggiungi timestamp per status
        if ticket_data['status'] == 'IN_LAVORAZIONE':
            ticket.started_at = created_at + timedelta(hours=random.randint(2, 12))
        elif ticket_data['status'] == 'RISOLTO':
            ticket.started_at = created_at + timedelta(hours=random.randint(1, 6))
            ticket.closed_at = ticket.started_at + timedelta(hours=random.randint(4, 48))
        
        db.session.add(ticket)
        db.session.flush()  # Flush per ottenere il ticket.id
        
        # Aggiungi commenti se presenti
        if 'comments' in ticket_data:
            for author_name, comment_text in ticket_data['comments']:
                comment = Comment(
                    ticket_id=ticket.id,
                    author_name=author_name,
                    body=comment_text,
                    created_at=ticket.created_at + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(comment)
        
        created_tickets.append(ticket)
        
        status_emoji = "🆕" if ticket.status == "NUOVO" else "⚙️" if ticket.status == "IN_LAVORAZIONE" else "✅"
        print(f"{status_emoji} Ticket #{i+1}: {ticket_data['type']} - {ticket_data.get('anomaly_category', ticket_data.get('title'))}")
    
    db.session.commit()
    return created_tickets


def main():
    """Funzione principale per popolare il database"""
    print("=" * 60)
    print("POPOLAMENTO DATABASE CON DATI DI TEST")
    print("=" * 60)
    
    with app.app_context():
        # Crea utenti
        users = seed_users()
        
        # Crea ticket
        tickets = seed_tickets(users)
        
        print("\n" + "=" * 60)
        print("✅ COMPLETATO!")
        print(f"   • {len(users)} utenti creati/verificati")
        print(f"   • {len(tickets)} ticket creati")
        print("=" * 60)
        print("\nCredenziali utenti di test:")
        print("  - Username: mario.rossi   | Password: password123")
        print("  - Username: luca.bianchi  | Password: password123")
        print("  - Username: giulia.verdi  | Password: password123")
        print("\nPuoi ora accedere all'applicazione con questi utenti!")
        print("=" * 60)


if __name__ == '__main__':
    main()
