"""
Script per gestire utenti amministratori
Esegui: python manage_users.py
"""

from app import app, db, User
import sys


def list_users():
    """Elenca tutti gli utenti"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("❌ Nessun utente presente nel database.")
            return
        
        print("\n" + "=" * 60)
        print("LISTA UTENTI")
        print("=" * 60)
        for user in users:
            ticket_count = len(user.assigned_tickets)
            print(f"  ID: {user.id} | Username: {user.username} | Ticket assegnati: {ticket_count}")
        print("=" * 60 + "\n")


def add_user():
    """Aggiungi un nuovo utente"""
    print("\n" + "=" * 60)
    print("AGGIUNGI NUOVO UTENTE")
    print("=" * 60)
    
    username = input("Inserisci username: ").strip()
    
    if not username:
        print(" Username non può essere vuoto!")
        return
    
    with app.app_context():
        # Verifica se esiste già
        existing = User.query.filter_by(username=username).first()
        if existing:
            print(f" L'utente '{username}' esiste già!")
            return
        
        password = input("Inserisci password: ").strip()
        
        if not password:
            print(" Password non può essere vuota!")
            return
        
        # Crea nuovo utente
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        print(f" Utente '{username}' creato con successo!")
        print("=" * 60 + "\n")


def delete_user():
    """Elimina un utente"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print(" Nessun utente presente nel database.")
            return
        
        print("\n" + "=" * 60)
        print("ELIMINA UTENTE")
        print("=" * 60)
        
        # Mostra lista utenti
        for user in users:
            ticket_count = len(user.assigned_tickets)
            print(f"  ID: {user.id} | Username: {user.username} | Ticket assegnati: {ticket_count}")
        
        print("=" * 60)
        
        try:
            user_id = input("\nInserisci ID utente da eliminare (0 per annullare): ").strip()
            user_id = int(user_id)
            
            if user_id == 0:
                print("Operazione annullata.")
                return
            
            user = User.query.get(user_id)
            
            if not user:
                print(f" Utente con ID {user_id} non trovato!")
                return
            
            # Conferma eliminazione
            confirm = input(f"  Sei sicuro di voler eliminare '{user.username}'? (si/no): ").strip().lower()
            
            if confirm == 'si':
                username = user.username
                
                # I ticket assegnati a questo utente diventeranno non assegnati (assigned_to_id = NULL)
                # Questo è automatico con la relazione ForeignKey
                
                db.session.delete(user)
                db.session.commit()
                
                print(f" Utente '{username}' eliminato con successo!")
                print("   (I ticket assegnati sono stati liberati)")
            else:
                print("Operazione annullata.")
            
        except ValueError:
            print(" ID non valido!")
        except Exception as e:
            print(f" Errore: {e}")
        
        print("=" * 60 + "\n")


def change_password():
    """Cambia password di un utente"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print(" Nessun utente presente nel database.")
            return
        
        print("\n" + "=" * 60)
        print("CAMBIA PASSWORD UTENTE")
        print("=" * 60)
        
        # Mostra lista utenti
        for user in users:
            print(f"  ID: {user.id} | Username: {user.username}")
        
        print("=" * 60)
        
        try:
            user_id = input("\nInserisci ID utente (0 per annullare): ").strip()
            user_id = int(user_id)
            
            if user_id == 0:
                print("Operazione annullata.")
                return
            
            user = User.query.get(user_id)
            
            if not user:
                print(f" Utente con ID {user_id} non trovato!")
                return
            
            new_password = input(f"Inserisci nuova password per '{user.username}': ").strip()
            
            if not new_password:
                print(" Password non può essere vuota!")
                return
            
            user.set_password(new_password)
            db.session.commit()
            
            print(f" Password cambiata con successo per '{user.username}'!")
            
        except ValueError:
            print(" ID non valido!")
        except Exception as e:
            print(f" Errore: {e}")
        
        print("=" * 60 + "\n")


def show_menu():
    """Mostra il menu principale"""
    print("\n" + "=" * 60)
    print("GESTIONE UTENTI - FIXIT")
    print("=" * 60)
    print("1. Lista utenti")
    print("2. Aggiungi nuovo utente")
    print("3. Elimina utente")
    print("4. Cambia password utente")
    print("0. Esci")
    print("=" * 60)


def main():
    """Funzione principale"""
    while True:
        show_menu()
        choice = input("\nScegli un'opzione: ").strip()
        
        if choice == '1':
            list_users()
        elif choice == '2':
            add_user()
        elif choice == '3':
            delete_user()
        elif choice == '4':
            change_password()
        elif choice == '0':
            print("\n Arrivederci!")
            break
        else:
            print(" Opzione non valida!")
        
        input("\nPremi INVIO per continuare...")


if __name__ == '__main__':
    main()
