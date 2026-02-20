import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-CHANGE-IN-PRODUCTION')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# ==================== MODELS ====================

class User(db.Model):
    """Admin User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationship
    assigned_tickets = db.relationship('Ticket', backref='assigned_to', lazy=True, foreign_keys='Ticket.assigned_to_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Ticket(db.Model):
    """Ticket Model for both MEZZO and TECNICO types"""
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_type = db.Column(db.String(20), nullable=False)  # 'MEZZO' or 'TECNICO'
    status = db.Column(db.String(20), default='NUOVO', nullable=False)  # 'NUOVO', 'IN_LAVORAZIONE', 'RISOLTO'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    started_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # Common fields
    requester_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # MEZZO-specific fields
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_number = db.Column(db.String(50), nullable=True)
    anomaly_category = db.Column(db.String(100), nullable=True)
    
    # TECNICO-specific fields
    department = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(200), nullable=True)
    priority = db.Column(db.String(20), nullable=True)  # 'BASSA', 'MEDIA', 'ALTA'

    # Comments relationship
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Ticket {self.id} - {self.ticket_type}>'


class Comment(db.Model):
    """Comments added by operators on tickets"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_name = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<Comment {self.id} on Ticket {self.ticket_id}>'


# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def login_required(f):
    """Decorator to require login for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Devi effettuare il login per accedere a questa pagina.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f):
    """Decorator to require superuser role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_superuser'):
            flash('Permesso negato: funzionalità riservata agli amministratori.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Homepage with ticket type selection"""
    return render_template('index.html')


@app.route('/new/mezzi', methods=['GET', 'POST'])
def new_mezzi():
    """Form for Vehicle Intervention tickets"""
    if request.method == 'POST':
        # Get form data
        requester_name = request.form.get('requester_name')
        vehicle_type = request.form.get('vehicle_type')
        vehicle_number = request.form.get('vehicle_number')
        anomaly_category = request.form.get('anomaly_category')
        description = request.form.get('description')
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Create new ticket
        ticket = Ticket(
            ticket_type='MEZZO',
            requester_name=requester_name,
            vehicle_type=vehicle_type,
            vehicle_number=vehicle_number,
            anomaly_category=anomaly_category,
            description=description,
            image_filename=image_filename
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash(f'Ticket #{ticket.id} creato con successo!', 'success')
        return redirect(url_for('index'))
    
    # Anomaly categories
    anomaly_categories = [
        "Livello Olio/Liquidi",
        "Perdite Liquidi",
        "Pneumatici",
        "Carrozzeria",
        "Spie/Allarmi",
        "Dispositivi Segnalazione",
        "Freni/Sterzo/Cambio",
        "Braccio/Spreader",
        "Rumori Insoliti",
        "Incidenti/Danni",
        "Altri Problemi"
    ]
    
    return render_template('form_mezzi.html', anomaly_categories=anomaly_categories)


@app.route('/new/tecnico', methods=['GET', 'POST'])
def new_tecnico():
    """Form for Technical Intervention tickets"""
    if request.method == 'POST':
        # Get form data
        requester_name = request.form.get('requester_name')
        title = request.form.get('title')
        priority = request.form.get('priority')
        description = request.form.get('description')
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Create new ticket
        ticket = Ticket(
            ticket_type='TECNICO',
            requester_name=requester_name,
            title=title,
            priority=priority,
            description=description,
            image_filename=image_filename
        )
        
        db.session.add(ticket)
        db.session.commit()
        
        flash(f'Ticket #{ticket.id} creato con successo!', 'success')
        return redirect(url_for('index'))
    
    return render_template('form_tecnico.html')


# ==================== ADMIN ROUTES ====================

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_superuser'] = user.is_superuser
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenziali non valide.', 'danger')
    
    return render_template('login.html')


@app.route('/admin/logout')
@login_required
def logout():
    """Admin logout"""
    session.clear()
    flash('Logout effettuato con successo.', 'info')
    return redirect(url_for('index'))


@app.route('/admin/dashboard')
@login_required
def dashboard():
    """Admin dashboard with ticket list and filters"""
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    assigned_filter = request.args.get('assigned', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Base query
    query = Ticket.query
    
    # Apply filters
    if search_query:
        query = query.filter(
            db.or_(
                Ticket.id == int(search_query) if search_query.isdigit() else False,
                Ticket.requester_name.ilike(f'%{search_query}%'),
                Ticket.description.ilike(f'%{search_query}%')
            )
        )
    
    if status_filter:
        query = query.filter(Ticket.status == status_filter)
    
    if assigned_filter:
        if assigned_filter == 'unassigned':
            query = query.filter(Ticket.assigned_to_id.is_(None))
        else:
            query = query.filter(Ticket.assigned_to_id == int(assigned_filter))
    
    # Sort by newest first with pagination
    pagination = query.order_by(Ticket.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    tickets = pagination.items
    
    # Get all admins for filter dropdown
    admins = User.query.all()
    
    return render_template('dashboard.html', tickets=tickets, admins=admins, pagination=pagination, per_page=per_page)


@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@superuser_required
def manage_users():
    """Superuser-only user management view"""
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            is_super = True if request.form.get('is_superuser') == 'on' else False

            if not username or not password:
                flash('Username e password sono obbligatori.', 'danger')
            elif User.query.filter_by(username=username).first():
                flash('Username già esistente.', 'warning')
            else:
                new_user = User(username=username, is_superuser=is_super)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                flash('Utente creato con successo.', 'success')

        elif action == 'delete':
            user_id = request.form.get('user_id')
            if user_id:
                user = User.query.get(int(user_id))
                if not user:
                    flash('Utente non trovato.', 'danger')
                elif user.id == session.get('user_id'):
                    flash('Non puoi eliminare il tuo stesso account.', 'warning')
                else:
                    db.session.delete(user)
                    db.session.commit()
                    flash('Utente eliminato con successo.', 'success')

        elif action == 'reset_password':
            user_id = request.form.get('user_id')
            new_password = request.form.get('new_password', '').strip()
            if not new_password:
                flash('La nuova password è obbligatoria.', 'danger')
            else:
                user = User.query.get(int(user_id)) if user_id else None
                if not user:
                    flash('Utente non trovato.', 'danger')
                else:
                    user.set_password(new_password)
                    db.session.commit()
                    flash('Password aggiornata con successo.', 'success')

        return redirect(url_for('manage_users'))

    users = User.query.order_by(User.username).all()
    return render_template('users.html', users=users)


@app.route('/admin/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    """View and edit ticket details"""
    ticket = Ticket.query.get_or_404(ticket_id)
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_at.desc()).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_status':
            new_status = request.form.get('status')
            old_status = ticket.status
            ticket.status = new_status
            
            # Update timestamps based on status change
            if new_status == 'IN_LAVORAZIONE' and old_status == 'NUOVO':
                ticket.started_at = datetime.utcnow()
            elif new_status == 'RISOLTO' and old_status != 'RISOLTO':
                ticket.closed_at = datetime.utcnow()
            
            db.session.commit()
            flash('Status aggiornato con successo!', 'success')
        
        elif action == 'assign':
            assigned_id = request.form.get('assigned_to_id')
            if assigned_id:
                ticket.assigned_to_id = int(assigned_id) if assigned_id != 'none' else None
            else:
                ticket.assigned_to_id = None
            
            db.session.commit()
            flash('Assegnazione aggiornata con successo!', 'success')
        
        elif action == 'delete':
            # Delete associated image if exists
            if ticket.image_filename:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], ticket.image_filename)
                if os.path.exists(image_path):
                    os.remove(image_path)
            
            db.session.delete(ticket)
            db.session.commit()
            flash('Ticket eliminato con successo!', 'success')
            return redirect(url_for('dashboard'))

        elif action == 'add_comment':
            author_name = request.form.get('author_name', '').strip()
            body = request.form.get('comment_body', '').strip()

            if not author_name or not body:
                flash('Nome e commento sono obbligatori.', 'danger')
            else:
                comment = Comment(ticket_id=ticket.id, author_name=author_name, body=body)
                db.session.add(comment)
                db.session.commit()
                flash('Commento aggiunto con successo.', 'success')

        elif action == 'update_priority':
            if ticket.ticket_type != 'TECNICO':
                flash('La priorità è modificabile solo per i ticket tecnici.', 'warning')
            else:
                new_priority = request.form.get('priority')
                if new_priority not in {'BASSA', 'MEDIA', 'ALTA'}:
                    flash('Priorità non valida.', 'danger')
                else:
                    ticket.priority = new_priority
                    db.session.commit()
                    flash('Priorità aggiornata con successo.', 'success')
        
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    
    # Get all admins for assignment dropdown
    admins = User.query.all()
    
    return render_template('ticket_detail.html', ticket=ticket, admins=admins, comments=comments)


# ==================== DATABASE INITIALIZATION ====================

def init_db():
    """Initialize database and create default admin user"""
    with app.app_context():
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin')
            admin.set_password('admin123')
            admin.is_superuser = True
            db.session.add(admin)
            db.session.commit()
            print('Default admin user created: admin/admin123')
        else:
            # Ensure admin retains superuser status
            if not admin.is_superuser:
                admin.is_superuser = True
                db.session.commit()
            print('Admin user already exists.')


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
