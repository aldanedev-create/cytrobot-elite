import re
from datetime import datetime, timedelta
from database.models import User

class RegisterHandler:
    def __init__(self, db, User, ActivityLogger):
        self.db = db
        self.User = User
        self.ActivityLogger = ActivityLogger
    
    def register_user(self, email, username, password, confirm_password, ip_address):
        # Validation
        if not email or not username or not password:
            return False, "All fields are required"
        
        if password != confirm_password:
            return False, "Passwords do not match"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email format"
        
        if len(username) < 3 or len(username) > 50:
            return False, "Username must be between 3 and 50 characters"
        
        # Check if user exists
        if self.User.query.filter_by(email=email).first():
            return False, "Email already registered"
        
        if self.User.query.filter_by(username=username).first():
            return False, "Username already taken"
        
        # Create user
        user = self.User(
            email=email,
            username=username,
            role='user',
            subscription_status='inactive',
            is_active=True,
            is_blocked=False
        )
        user.set_password(password)
        
        self.db.session.add(user)
        self.db.session.commit()
        
        self.ActivityLogger.log_activity(user.id, 'REGISTER', f'User registered from {ip_address}', ip_address)
        
        return True, user