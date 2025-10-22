from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User, db
from forms import LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Halaman login untuk Personal Trainer
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Selamat datang, {user.full_name}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Username atau password salah.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Logout user
    """
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/create-admin')
def create_admin():
    """
    Route untuk membuat admin pertama (hanya untuk development)
    Route ini otomatis dinonaktifkan di production untuk keamanan
    """
    from config import Config
    
    # Nonaktifkan route ini di production
    if Config.PRODUCTION:
        flash('Route ini tidak tersedia di production.', 'error')
        return redirect(url_for('auth.login'))
    
    existing_admin = User.query.first()
    if existing_admin:
        flash('Admin sudah ada!', 'error')
        return redirect(url_for('auth.login'))
    
    admin = User(
        username='admin',
        email='admin@gym.com',
        full_name='Administrator'
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    flash('Admin berhasil dibuat! Username: admin, Password: admin123', 'success')
    return redirect(url_for('auth.login'))