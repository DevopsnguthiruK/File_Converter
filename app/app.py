from flask import Flask, render_template, send_from_directory
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
import logging
import os
from app.config import Config
from app.models import db, User
from app.routes.auth_route import auth_route
from app.routes.converter import converter_route

def seed_initial_users():
    """
    Seed initial users in the database if no users exist
    """
    existing_users = User.query.count()
    if existing_users > 0:
        logging.info("Database already has users. Skipping seeding.")
        return

    initial_users = [
        {
            'user_id': 'A003',
            'username': 'Steve',
            'email': 'admin@enterprise.com',
            'password': 'Admin@2025!',
            'is_admin': True
        },
        {
            'user_id': 'D004',
            'username': 'Joe',
            'email': 'datauser@enterprise.com',
            'password': 'DataUser@2025!',
            'is_admin': False
        }
    ]

    try:
        for user_data in initial_users:
            hashed_password = generate_password_hash(user_data['password'])
            
            new_user = User(
                user_id=user_data['user_id'],
                username=user_data['username'],
                email=user_data['email'],
                password=hashed_password,
                is_admin=user_data['is_admin']
            )
            
            db.session.add(new_user)
        
        db.session.commit()
        logging.info("Initial users seeded successfully")
    
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error seeding users: {str(e)}")

def create_app(config_class=Config):
    app = Flask(__name__, 
                static_folder='static', 
                template_folder='templates')
    app.config.from_object(config_class)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Register blueprints
    app.register_blueprint(auth_route, url_prefix='/api/auth')
    app.register_blueprint(converter_route, url_prefix='/api/converter')

    # Root route to serve login page
    @app.route('/')
    def login_page():
        return render_template('login.html')

    # Dashboard route
    @app.route('/dashboard')
    def dashboard():
        return render_template('index.html')
    
    # Conversion route
    @app.route('/conversion-result')
    def conversion_result_page():
        return render_template('conversion-result.html')

    # Static file serving route
    @app.route('/static/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)

    # Create tables
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Seed initial users
        seed_initial_users()
        
        # Ensure upload directory exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app