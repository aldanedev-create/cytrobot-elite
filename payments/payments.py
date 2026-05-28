import secrets
from datetime import datetime, timedelta

class PaymentProcessor:
    def __init__(self, db, Payment, Subscription, User, ActivityLogger):
        self.db = db
        self.Payment = Payment
        self.Subscription = Subscription
        self.User = User
        self.ActivityLogger = ActivityLogger
    
    def create_payment(self, user_id, amount, discount_code=None):
        transaction_id = secrets.token_hex(16)
        
        payment = self.Payment(
            user_id=user_id,
            amount=amount,
            status='pending',
            transaction_id=transaction_id,
            discount_code=discount_code
        )
        
        self.db.session.add(payment)
        self.db.session.commit()
        
        return payment
    
    def complete_payment(self, transaction_id, admin_id=None):
        payment = self.Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return False, "Payment not found"
        
        payment.status = 'completed'
        
        # Activate subscription
        user = self.User.query.get(payment.user_id)
        user.subscription_status = 'active'
        
        subscription = self.Subscription(
            user_id=payment.user_id,
            plan='basic',
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        
        self.db.session.add(subscription)
        self.db.session.commit()
        
        if admin_id:
            self.ActivityLogger.log_activity(
                admin_id,
                'COMPLETE_PAYMENT',
                f'Completed payment {transaction_id} for user {user.email}',
                None
            )
        
        return True, "Payment completed"
    
    def refund_payment(self, transaction_id, admin_id):
        payment = self.Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            return False, "Payment not found"
        
        payment.status = 'refunded'
        self.db.session.commit()
        
        self.ActivityLogger.log_activity(
            admin_id,
            'REFUND_PAYMENT',
            f'Refunded payment {transaction_id}',
            None
        )
        
        return True, "Payment refunded"
