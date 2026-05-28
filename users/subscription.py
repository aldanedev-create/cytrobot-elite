from datetime import datetime, timedelta
from database.models import Subscription, Payment
import secrets

class SubscriptionHandler:
    def __init__(self, db, User, Subscription, Payment):
        self.db = db
        self.User = User
        self.Subscription = Subscription
        self.Payment = Payment
    
    def create_subscription(self, user_id, plan, discount_code=None):
        user = self.User.query.get(user_id)
        if not user:
            return False, "User not found"
        if plan != 'basic':
            return False, "Invalid subscription plan"
        
        price = 5  # Basic plan price
        
        # Apply discount
        if discount_code:
            discount = self.validate_discount(discount_code)
            if discount:
                price = price * (100 - discount.discount_percent) / 100
        
        # Create pending payment record. A webhook/admin confirmation activates the subscription.
        transaction_id = secrets.token_hex(16)
        payment = self.Payment(
            user_id=user_id,
            amount=price,
            status='pending',
            transaction_id=transaction_id,
            discount_code=discount_code
        )
        
        self.db.session.add(payment)
        self.db.session.commit()

        return True, {
            "message": f"Payment created. Please complete payment of ${price:.2f}.",
            "payment": payment
        }

    def confirm_payment(self, transaction_id):
        payment = self.Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return False, "Payment not found"

        user = self.User.query.get(payment.user_id)
        if not user:
            return False, "User not found"

        if payment.status == 'completed':
            return True, "Payment already confirmed"

        payment.status = 'completed'

        old_subscriptions = self.Subscription.query.filter_by(user_id=user.id, is_active=True).all()
        for subscription in old_subscriptions:
            subscription.is_active = False

        subscription = self.Subscription(
            user_id=user.id,
            plan='basic',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        self.db.session.add(subscription)
        user.subscription_status = 'active'
        self.db.session.commit()

        return True, "Payment confirmed and subscription activated"
    
    def create_demo(self, user_id):
        user = self.User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        expiry = datetime.utcnow() + timedelta(days=5)
        user.subscription_status = 'demo'
        user.demo_expiry = expiry
        
        subscription = self.Subscription(
            user_id=user_id,
            plan='demo',
            start_date=datetime.utcnow(),
            end_date=expiry,
            is_active=True
        )
        
        self.db.session.add(subscription)
        self.db.session.commit()
        
        return True, "Demo activated for 5 days"
    
    def validate_discount(self, code):
        from database.models import DiscountCode
        discount = DiscountCode.query.filter_by(code=code, is_active=True).first()
        
        if discount and (not discount.expires_at or discount.expires_at > datetime.utcnow()):
            return discount
        
        return None
    
    def check_subscription_status(self, user_id):
        user = self.User.query.get(user_id)
        
        if user.role in ['super_admin', 'admin']:
            return True, "Admin access"
        
        if user.subscription_status == 'active':
            subscription = self.Subscription.query.filter_by(
                user_id=user_id, 
                is_active=True
            ).first()
            
            if subscription and subscription.end_date > datetime.utcnow():
                return True, "Active subscription"
            else:
                user.subscription_status = 'inactive'
                self.db.session.commit()
                return False, "Subscription expired"
        
        elif user.subscription_status == 'demo':
            if user.demo_expiry and user.demo_expiry > datetime.utcnow():
                return True, f"Demo active until {user.demo_expiry.strftime('%Y-%m-%d')}"
            else:
                user.subscription_status = 'inactive'
                self.db.session.commit()
                return False, "Demo expired"
        
        return False, "No active subscription"
