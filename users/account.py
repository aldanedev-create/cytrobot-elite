from datetime import datetime

class AccountManager:
    def __init__(self, db, User, ActivityLogger):
        self.db = db
        self.User = User
        self.ActivityLogger = ActivityLogger
    
    def update_profile(self, user_id, data, ip_address=None):
        user = self.User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'telegram_chat_id' in data:
            user.telegram_chat_id = data['telegram_chat_id']
        
        self.db.session.commit()
        
        self.ActivityLogger.log_activity(
            user_id,
            'UPDATE_PROFILE',
            f'Updated profile information',
            ip_address
        )
        
        return True, "Profile updated"
    
    def change_password(self, user_id, current_password, new_password, ip_address=None):
        user = self.User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        if not user.check_password(current_password):
            return False, "Current password is incorrect"
        
        if len(new_password) < 8:
            return False, "Password must be at least 8 characters"
        
        user.set_password(new_password)
        self.db.session.commit()
        
        self.ActivityLogger.log_activity(
            user_id,
            'CHANGE_PASSWORD',
            f'Changed password',
            ip_address
        )
        
        return True, "Password changed"