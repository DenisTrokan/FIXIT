"""
Script di test per la connessione SMTP con Flask-Mail
Testa la connessione al server mail.dk.dfds.root senza autenticazione
"""

from flask import Flask
from flask_mail import Mail, Message

# Configurazione Flask
app = Flask(__name__)

# Configurazione SMTP SENZA PASSWORD
app.config['MAIL_SERVER'] = 'mail.dk.dfds.root'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_DEFAULT_SENDER'] = 'FIXIT@dfds.com'

# Inizializza Mail
mail = Mail(app)

SENDER_EMAIL = "FIXIT@dfds.com"
RECIPIENT_EMAIL = "denitro@dfds.com"

print("=" * 60)
print("🧪 TEST CONNESSIONE SMTP CON FLASK-MAIL")
print("=" * 60)

try:
    print(f"\n🔌 Configurazione:")
    print(f"   Server: {app.config['MAIL_SERVER']}")
    print(f"   Porta: {app.config['MAIL_PORT']}")
    print(f"   TLS: {app.config['MAIL_USE_TLS']}")
    print(f"   Mittente: {SENDER_EMAIL}")
    
    print(f"\n📧 Invio email di test...")
    
    with app.app_context():
        # Composizione email di test
        msg = Message(
            subject='🧪 Test Email - Sistema Ticketing',
            recipients=[RECIPIENT_EMAIL],
            html="""
            <html>
              <body style="font-family: Arial; line-height: 1.6;">
                <h2>Test Email SMTP</h2>
                <p>Questa è una email di test dal sistema ticketing FIXIT.</p>
                <p><strong>Status:</strong> ✓ Connessione funzionante</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                  <strong>Mittente:</strong> FIXIT@dfds.com<br>
                  <strong>Destinatario:</strong> denitro@dfds.com<br>
                  <strong>Server:</strong> mail.dk.dfds.root:25<br>
                  <strong>Autenticazione:</strong> No (Relay)
                </p>
              </body>
            </html>
            """
        )
        
        mail.send(msg)
    
    print("✓ Email inviata con successo!")
    print(f"   Da: {SENDER_EMAIL}")
    print(f"   A:  {RECIPIENT_EMAIL}")
    
    print("\n" + "=" * 60)
    print("✅ TEST COMPLETATO CON SUCCESSO")
    print("=" * 60)
    
except Exception as e:
    import traceback
    print(f"\n❌ Errore: {e}")
    print("\nTraceback completo:")
    traceback.print_exc()
    print("\n" + "=" * 60)
    print("TROUBLESHOOTING:")
    print("- Verifica che mail.dk.dfds.root sia raggiungibile")
    print("- Controlla che la porta 25 non sia bloccata dal firewall")
    print("- Verifica l'email mittente FIXIT@dfds.com")
    print("- Installa Flask-Mail: pip install Flask-Mail")
    print("=" * 60)
