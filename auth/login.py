from datetime import datetime, timedelta
from flask_login import login_user
from database.models import User, SecurityEvent

class LoginHandler:
    def __init__(self, db, SecurityEvent, ActivityLogger):
        self.db = db
        self.SecurityEvent = SecurityEvent
        self.ActivityLogger = ActivityLogger
    
    def authenticate(self, email, password, ip_address, user_agent):
        user = User.query.filter_by(email=email).first()
        
        if not user:
            self._log_security_event('FAILED_LOGIN', 'warning', f'Failed login attempt for non-existent email: {email}', ip_address)
            return False, "Invalid email or password"
        
        if user.is_blocked:
            self._log_security_event('BLOCKED_LOGIN', 'critical', f'Blocked user attempted login: {email}', ip_address, user.id)
            return False, "Your account has been blocked. Contact support."
        
        if not user.check_password(password):
            self._log_security_event('FAILED_LOGIN', 'warning', f'Failed password attempt for user: {email}', ip_address, user.id)
            
            # Check for brute force
            recent_failures = self.SecurityEvent.query.filter_by(
                user_id=user.id, 
                event_type='FAILED_LOGIN'
            ).filter(
                self.SecurityEvent.timestamp > datetime.utcnow() - timedelta(minutes=15)
            ).count()
            
            if recent_failures >= 5:
                user.is_blocked = True
                self.db.session.commit()
                self._log_security_event('BRUTE_FORCE', 'critical', f'Brute force detected for user: {email}', ip_address, user.id)
                return False, "Too many failed attempts. Account blocked."
            
            return False, "Invalid email or password"
        
        # Successful login
        self.ActivityLogger.log_activity(user.id, 'LOGIN', f'User logged in from {ip_address}', ip_address)
        self._log_security_event('SUCCESSFUL_LOGIN', 'info', f'Successful login', ip_address, user.id)
        
        user.last_login = datetime.utcnow()
        self.db.session.commit()
        
        return True, user
    
    def _log_security_event(self, event_type, severity, description, ip_address, user_id=None):
        event = self.SecurityEvent(
            event_type=event_type,
            severity=severity,
            description=description,
            ip_address=ip_address,
            user_id=user_id,
            timestamp=datetime.utcnow()
        )
        self.db.session.add(event)
        self.db.session.commit()
