from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

# Add login manager configuration
login_manager.login_view = 'main.login'  # Route for unauthenticated users
login_manager.login_message_category = 'info'  # Style for flashed messages