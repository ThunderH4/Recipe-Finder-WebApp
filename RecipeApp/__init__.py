from flask import Flask
from .config import Config
from .extensions import db, login_manager, bcrypt
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    
    # Import models here
    from .models import User
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)
    
    return app