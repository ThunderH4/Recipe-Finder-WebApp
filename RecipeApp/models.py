from datetime import timezone, datetime
from RecipeApp.extensions import db, bcrypt
from flask_login import UserMixin
from .extensions import login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    max_time = db.Column(db.Integer)
    difficulty = db.Column(db.String(50))
    diet = db.Column(db.String(50))
    allergies = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship (optional but useful)
    user = db.relationship('User', backref=db.backref('preferences', lazy=True))


# Add user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



