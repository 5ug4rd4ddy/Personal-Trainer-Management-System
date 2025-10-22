from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import User, Client, Assessment, Session, WorkoutPlan, db
from datetime import datetime, timedelta
from sqlalchemy import desc

client_portal_bp = Blueprint('client_portal', __name__)

def client_required(f):
    """
    Decorator untuk memastikan user adalah klien atau admin
    """
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        
        # Admin bisa mengakses semua
        if current_user.is_admin():
            return f(*args, **kwargs)
        
        # Client hanya bisa mengakses data sendiri
        if current_user.is_client():
            client_id = kwargs.get('client_id')
            if client_id and current_user.client_id != client_id:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        
        abort(403)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@client_portal_bp.route('/my-profile')
@login_required
@client_required
def my_profile():
    """
    Halaman profil klien - hanya untuk role client
    """
    if current_user.is_admin():
        flash('Halaman ini khusus untuk klien.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if not current_user.client_id:
        flash('Akun Anda belum terhubung dengan data klien.', 'error')
        return redirect(url_for('main.dashboard'))
    
    client = Client.query.get_or_404(current_user.client_id)
    
    # Ambil data terkait
    latest_assessment = Assessment.query.filter_by(client_id=client.id).order_by(desc(Assessment.created_at)).first()
    recent_sessions = Session.query.filter_by(client_id=client.id).order_by(desc(Session.date)).limit(10).all()
    workout_plans = WorkoutPlan.query.filter_by(client_id=client.id).order_by(desc(WorkoutPlan.created_at)).all()
    
    # Hitung umur jika ada tanggal lahir
    age = None
    if client.birth_date:
        today = datetime.now().date()
        age = today.year - client.birth_date.year - ((today.month, today.day) < (client.birth_date.month, client.birth_date.day))
    
    return render_template('client_portal/profile.html',
                         client=client,
                         age=age,
                         latest_assessment=latest_assessment,
                         recent_sessions=recent_sessions,
                         workout_plans=workout_plans)


@client_portal_bp.route('/my-sessions')
@login_required
@client_required
def my_sessions():
    """
    Halaman sesi latihan klien
    """
    if current_user.is_admin():
        flash('Halaman ini khusus untuk klien.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if not current_user.client_id:
        flash('Akun Anda belum terhubung dengan data klien.', 'error')
        return redirect(url_for('main.dashboard'))
    
    client = Client.query.get_or_404(current_user.client_id)
    
    # Pagination and filtering
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', '', type=str)
    
    query = Session.query.filter_by(client_id=client.id)
    
    # Filter by month if provided
    if month:
        try:
            month_date = datetime.strptime(month, '%Y-%m')
            start_date = month_date.date()
            if month_date.month == 12:
                end_date = datetime(month_date.year + 1, 1, 1).date()
            else:
                end_date = datetime(month_date.year, month_date.month + 1, 1).date()
            
            query = query.filter(Session.date >= start_date, Session.date < end_date)
        except ValueError:
            pass
    
    sessions = query.order_by(desc(Session.date)).paginate(
        page=page, per_page=15, error_out=False
    )
    
    return render_template('client_portal/sessions.html', 
                         client=client, 
                         sessions=sessions, 
                         selected_month=month)

@client_portal_bp.route('/my-workout-plans')
@login_required
@client_required
def my_workout_plans():
    """
    Halaman program latihan klien
    """
    if current_user.is_admin():
        flash('Halaman ini khusus untuk klien.', 'info')
        return redirect(url_for('main.dashboard'))
    
    if not current_user.client_id:
        flash('Akun Anda belum terhubung dengan data klien.', 'error')
        return redirect(url_for('main.dashboard'))
    
    client = Client.query.get_or_404(current_user.client_id)
    workout_plans = WorkoutPlan.query.filter_by(client_id=client.id).order_by(desc(WorkoutPlan.created_at)).all()
    
    return render_template('client_portal/workout_plans.html', 
                         client=client, 
                         workout_plans=workout_plans)