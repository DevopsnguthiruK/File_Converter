from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

class AuthService:
    def register_user(self, user_id, username, password, email, is_admin=False):
        """
        Register a new user
        
        Args:
            username (str): Username
            password (str): Password
            email (str): Email address
            is_admin (bool, optional): Admin status. Defaults to False.
        
        Returns:
            User: Newly created user
        
        Raises:
            ValueError: If username or email already exists
        """
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already exists')
        
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already exists')
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = User(
            user_id=user_id,
            username=username, 
            password=hashed_password, 
            email=email,
            is_admin=is_admin
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Registration failed')

    def authenticate_user(self, username, password):
        """
        Authenticate a user
        
        Args:
            username (str): Username
            password (str): Password
        
        Returns:
            User: Authenticated user
        
        Raises:
            ValueError: If credentials are invalid
        """
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password, password):
            raise ValueError('Invalid credentials')
        
        return user

    def get_user_by_username(self, username):
        """
        Retrieve user by username
        
        Args:
            username (str): Username to search for
        
        Returns:
            User: User object
        
        Raises:
            ValueError: If user not found
        """
        user = User.query.filter_by(username=username).first()
        
        if not user:
            raise ValueError('User not found')
        
        return user