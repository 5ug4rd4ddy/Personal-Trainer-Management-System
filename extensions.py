from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

# Shared extension instances to avoid circular imports
login_manager = LoginManager()
csrf = CSRFProtect()