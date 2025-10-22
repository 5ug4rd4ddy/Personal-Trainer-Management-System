import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Konfigurasi aplikasi Flask untuk Sistem Catatan Klien Personal Trainer
    Menggunakan environment variables untuk keamanan
    """
    # Secret key untuk session dan CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Environment settings
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    PRODUCTION = os.environ.get('PRODUCTION', 'False').lower() == 'true'
    
    # Database configuration - menggunakan environment variables
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'gym')
    
    # Check if using SQLite (for testing)
    if MYSQL_DB.startswith('sqlite:'):
        SQLALCHEMY_DATABASE_URI = MYSQL_DB
    else:
        # MySQL configuration
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}'
    
    # SQLAlchemy configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                os.environ.get('UPLOAD_FOLDER', 'static/uploads'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Session configuration
    session_hours = int(os.environ.get('PERMANENT_SESSION_LIFETIME_HOURS', 2))
    PERMANENT_SESSION_LIFETIME = timedelta(hours=session_hours)
    
    # Pagination
    CLIENTS_PER_PAGE = int(os.environ.get('CLIENTS_PER_PAGE', 10))
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        # Create upload directory if it doesn't exist
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)