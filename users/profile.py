class ProfileManager:
    def __init__(self, db, User):
        self.db = db
        self.User = User
    
    def get_profile(self, user_id):
        return self.User.query.get(user_id)
    
    def get_user_stats(self, user_id):
        from database.models import Trade, SignalHistory
        
        user = self.User.query.get(user_id)
        if not user:
            return None
        
        stats = {
            'total_signals': SignalHistory.query.filter_by(user_id=user_id).count(),
            'subscription_status': user.subscription_status,
            'member_since': user.created_at,
            'last_login': user.last_login
        }
        
        return stats