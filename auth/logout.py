from flask_login import logout_user

class LogoutHandler:
    def __init__(self, db, ActivityLogger):
        self.db = db
        self.ActivityLogger = ActivityLogger
    
    def logout(self, user_id, ip_address):
        self.ActivityLogger.log_activity(user_id, 'LOGOUT', f'User logged out', ip_address)
        logout_user()
        return True