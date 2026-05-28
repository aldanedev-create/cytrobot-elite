from datetime import datetime, timedelta

class SubscriptionManager:
    def __init__(self, db, Subscription, User):
        self.db = db
        self.Subscription = Subscription
        self.User = User
    
    def activate_subscription(self, user_id, plan, duration_days=30):
        user = self.User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        # Deactivate old subscriptions
        old_subs = self.Subscription.query.filter_by(user_id=user_id, is_active=True).all()
        for sub in old_subs:
            sub.is_active = False
        
        # Create new subscription
        end_date = datetime.utcnow() + timedelta(days=duration_days)
        subscription = self.Subscription(
            user_id=user_id,
            plan=plan,
            start_date=datetime.utcnow(),
            end_date=end_date,
            is_active=True
        )
        
        user.subscription_status = 'active'
        
        self.db.session.add(subscription)
        self.db.session.commit()
        
        return True, subscription
    
    def deactivate_subscription(self, user_id):
        user = self.User.query.get(user_id)
        if user:
            user.subscription_status = 'inactive'
            
            subscriptions = self.Subscription.query.filter_by(user_id=user_id, is_active=True).all()
            for sub in subscriptions:
                sub.is_active = False
            
            self.db.session.commit()
            return True
        
        return False
    
    def check_expired_subscriptions(self):
        expired = self.Subscription.query.filter(
            self.Subscription.end_date < datetime.utcnow(),
            self.Subscription.is_active == True
        ).all()
        
        for sub in expired:
            sub.is_active = False
            user = self.User.query.get(sub.user_id)
            if user and user.role == 'user':
                user.subscription_status = 'inactive'
        
        self.db.session.commit()
        return len(expired)