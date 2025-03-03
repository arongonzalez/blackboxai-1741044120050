from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'

    with app.app_context():
        # Import models and routes
        from . import models
        from . import routes
        
        # Initialize routes
        routes.init_routes(app)

        try:
            # Create database tables if they don't exist
            db.drop_all()
            db.create_all()

            # Create admin user if not exists
            admin = models.User.query.filter_by(username='admin').first()
            if not admin:
                from werkzeug.security import generate_password_hash
                admin = models.User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@example.com',
                    role='admin',
                    is_active=True
                )
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")

    return app

# Create the application instance
app = create_app()

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(int(user_id))
