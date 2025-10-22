from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from models import Client, Assessment, Session, db
from sqlalchemy import func, desc
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Halaman utama - redirect ke dashboard jika sudah login
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard utama - redirect berdasarkan role user
    """
    # Jika user adalah client, redirect ke profil client
    if current_user.is_client():
        return redirect(url_for('client_portal.my_profile'))
    
    # Jika user adalah admin, tampilkan dashboard admin
    if not current_user.is_admin():
        flash('Akses tidak diizinkan.', 'error')
        return redirect(url_for('auth.logout'))
    
    # Dashboard untuk admin
    total_clients = Client.query.count()
    total_assessments = Assessment.query.count()
    total_sessions = Session.query.count()
    
    # Recent clients (5 terbaru)
    recent_clients = Client.query.order_by(desc(Client.created_at)).limit(5).all()
    
    # Recent sessions (5 terbaru)
    recent_sessions = Session.query.order_by(desc(Session.created_at)).limit(5).all()
    
    
    # Monthly statistics
    current_month = datetime.now().replace(day=1)
    last_month = (current_month - timedelta(days=1)).replace(day=1)
    
    # New clients this month
    new_clients_this_month = Client.query.filter(Client.created_at >= current_month).count()
    new_clients_last_month = Client.query.filter(
        Client.created_at >= last_month,
        Client.created_at < current_month
    ).count()
    
    # Sessions this month
    sessions_this_month = Session.query.filter(Session.date >= current_month.date()).count()
    sessions_last_month = Session.query.filter(
        Session.date >= last_month.date(),
        Session.date < current_month.date()
    ).count()
    
    return render_template('dashboard.html',
                         total_clients=total_clients,
                         total_assessments=total_assessments,
                         total_sessions=total_sessions,
                         recent_clients=recent_clients,
                         recent_sessions=recent_sessions,
                         new_clients_this_month=new_clients_this_month,
                         new_clients_last_month=new_clients_last_month,
                         sessions_this_month=sessions_this_month,
                         sessions_last_month=sessions_last_month)