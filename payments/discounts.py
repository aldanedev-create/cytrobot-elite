import secrets
from datetime import datetime, timedelta

class DiscountManager:
    def __init__(self, db, DiscountCode, ActivityLogger):
        self.db = db
        self.DiscountCode = DiscountCode
        self.ActivityLogger = ActivityLogger
    
    def create_discount_code(self, discount_percent, expires_days=30, admin_id=None):
        code = secrets.token_hex(4).upper()
        
        expires_at = datetime.utcnow() + timedelta(days=expires_days) if expires_days else None
        
        discount = self.DiscountCode(
            code=code,
            discount_percent=discount_percent,
            expires_at=expires_at,
            created_by=admin_id
        )
        
        self.db.session.add(discount)
        self.db.session.commit()
        
        if admin_id:
            self.ActivityLogger.log_activity(
                admin_id,
                'CREATE_DISCOUNT',
                f'Created discount code {code} for {discount_percent}%',
                None
            )
        
        return discount
    
    def validate_discount(self, code):
        discount = self.DiscountCode.query.filter_by(code=code, is_active=True).first()
        
        if not discount:
            return None
        
        if discount.expires_at and discount.expires_at < datetime.utcnow():
            return None
        
        return discount
    
    def delete_discount_code(self, code, admin_id):
        discount = self.DiscountCode.query.filter_by(code=code).first()
        if discount:
            discount.is_active = False
            self.db.session.commit()
            
            self.ActivityLogger.log_activity(
                admin_id,
                'DELETE_DISCOUNT',
                f'Deleted discount code {code}',
                None
            )
            
            return True
        
        return False