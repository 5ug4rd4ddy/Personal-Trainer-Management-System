from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config

# Import db from models to avoid circular imports
from models import db

# Initialize other extensions
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """
    Factory function untuk membuat aplikasi Flask
    Sistem Catatan Klien Personal Trainer
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'
    login_manager.login_message_category = 'info'
    
    # User loader callback untuk Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        """
        Callback untuk memuat user berdasarkan ID dari session
        Diperlukan oleh Flask-Login untuk mengelola session user
        """
        from models import User
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.clients import clients_bp
    from routes.assessments import assessments_bp
    from routes.workout_plans import workout_plans_bp
    
    from routes.sessions import sessions_bp
    from routes.client_portal import client_portal_bp
    from routes.exercises import exercises_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(clients_bp, url_prefix='/clients')
    app.register_blueprint(assessments_bp, url_prefix='/assessments')
    app.register_blueprint(workout_plans_bp, url_prefix='/workout-plans')
    
    app.register_blueprint(sessions_bp, url_prefix='/sessions')
    app.register_blueprint(client_portal_bp, url_prefix='/client')
    app.register_blueprint(exercises_bp, url_prefix='/exercises')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Pastikan direktori uploads ada
    import os
    upload_folder = os.path.join(app.static_folder, 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8083)