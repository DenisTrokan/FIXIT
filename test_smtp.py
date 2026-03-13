"""
Script di test per la connessione SMTP con Flask-Mail
Testa la connessione SMTP autenticata (porta 587, STARTTLS)
"""

from flask import Flask
from flask_mail import Mail, Message

# Configurazione Flask
app = Flask(__name__)

# Configurazione SMTP CON AUTENTICAZIONE (porta 587 + TLS)
app.config['MAIL_SERVER'] = 'smtp.info-era.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seaports@smtp.info-era.com'
app.config['MAIL_PASSWORD'] = 'sea@Sea16'
app.config['MAIL_DEFAULT_SENDER'] = 'seaports@smtp.info-era.com'
app.config['MAIL_TIMEOUT'] = 10

# Inizializza Mail
mail = Mail(app)

SENDER_EMAIL = "seaports@smtp.info-era.com"
RECIPIENT_EMAIL = "denitro@dfds.com"

print("=" * 60)
print("🧪 TEST CONNESSIONE SMTP CON FLASK-MAIL")
print("=" * 60)

try:
    print(f"\n🔌 Configurazione:")
    print(f"   Server: {app.config['MAIL_SERVER']}")
    print(f"   Porta: {app.config['MAIL_PORT']}")
    print(f"   TLS: {app.config['MAIL_USE_TLS']}")
    print(f"   Username: {app.config['MAIL_USERNAME']}")
    print(f"   Mittente: {SENDER_EMAIL}")
    print(f"   Destinatario: {RECIPIENT_EMAIL}")
    
    print(f"\n📧 Invio email di test...")
    
    with app.app_context():
        # Composizione email di test
        msg = Message(
            subject='🧪 Test Email - FIXIT Sistema Ticketing',
            recipients=[RECIPIENT_EMAIL],
            html="""
            <html>
              <body style="font-family: Arial; line-height: 1.6;">
                <h2>Test Email SMTP Autenticato</h2>
                <p>Questa è una email di test dal sistema ticketing FIXIT.</p>
                <p><strong>Status:</strong> ✓ Connessione SMTP autenticata funzionante</p>
                <hr>
                <p style="color: #666; font-size: 12px;">
                  <strong>Mittente:</strong> seaports@smtp.info-era.com<br>
                  <strong>Destinatario:</strong> denitro@dfds.com<br>
                  <strong>Server:</strong> smtp.info-era.com:587<br>
                  <strong>Autenticazione:</strong> Sì (STARTTLS)
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
    print("- Verifica che smtp.info-era.com sia raggiungibile (porta 587)")
    print("- Controlla username/password")
    print("- Verifica che la porta 587 non sia bloccata dal firewall")
    print("- Installa Flask-Mail: pip install Flask-Mail")
    print("=" * 60)
