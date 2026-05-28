from datetime import datetime
from database.models import Trade, SignalHistory
from utils.helpers import generate_signal_message

class SignalManager:
    def __init__(self, db, Trade, Notifier, ActivityLogger):
        self.db = db
        self.Trade = Trade
        self.Notifier = Notifier
        self.ActivityLogger = ActivityLogger
    
    def create_manual_signal(self, pair, signal_type, entry_condition, tp, sl, admin_id):
        trade = self.Trade(
            pair=pair,
            signal_type=signal_type,
            entry_condition=entry_condition,
            tp=tp,
            sl=sl,
            created_by=admin_id,
            status='pending'
        )
        
        self.db.session.add(trade)
        self.db.session.commit()
        
        self.ActivityLogger.log_activity(
            admin_id, 
            'CREATE_SIGNAL', 
            f'Created {signal_type} signal for {pair}', 
            None
        )
        
        return True, trade
    
    def create_auto_signal(self, pair, signal_type, condition_description):
        trade = self.Trade(
            pair=pair,
            signal_type=signal_type,
            entry_condition=f"Auto-generated: {condition_description}",
            created_by=None,
            status='pending'
        )
        
        self.db.session.add(trade)
        self.db.session.commit()
        
        return True, trade
    
    def execute_signal(self, trade_id):
        trade = self.Trade.query.get(trade_id)
        if not trade or trade.status != 'pending':
            return False
        
        trade.status = 'executed'
        trade.executed_at = datetime.utcnow()
        self.db.session.commit()
        
        # Send to all subscribed users
        self._broadcast_signal(trade)
        
        return True
    
    def _broadcast_signal(self, trade):
        """Send signal to all eligible users"""
        from database.models import User
        
        message = generate_signal_message(trade)
        
        users = User.query.filter(
            User.is_active == True,
            User.is_blocked == False
        ).all()
        
        for user in users:
            # Check if user has access
            if user.has_access():
                # Send to Telegram
                if user.telegram_chat_id:
                    self.Notifier.send_telegram_signal(user.telegram_chat_id, message, trade)
                
                # Send to Email (optional)
                if user.email:
                    self.Notifier.send_email_signal(user.email, trade)
                
                # Log signal delivery
                history = SignalHistory(
                    user_id=user.id,
                    trade_id=trade.id,
                    delivered_via='telegram'
                )
                self.db.session.add(history)
        
        self.db.session.commit()
    
    def cancel_signal(self, trade_id, admin_id):
        trade = self.Trade.query.get(trade_id)
        if trade and trade.status == 'pending':
            trade.status = 'cancelled'
            self.db.session.commit()
            
            self.ActivityLogger.log_activity(
                admin_id,
                'CANCEL_SIGNAL',
                f'Cancelled signal for {trade.pair}',
                None
            )
            
            return True
        return False