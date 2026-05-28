from datetime import datetime, timedelta


def init_default_admin(db, User):
    """Initialize default super admin if none exists."""
    admin = User.query.filter_by(role='super_admin').first()

    if not admin:
        admin = User(
            email='aldanehutchinson5@gmail.com',
            username='superadmin',
            role='super_admin',
            subscription_status='active',
            is_active=True,
            is_blocked=False
        )
        admin.set_password('Admin123!')
        db.session.add(admin)
        db.session.commit()
        print("Default super admin created: aldanehutchinson5@gmail.com / Admin123!")


def calculate_expiry_date(days=30):
    """Calculate expiry date for subscription."""
    return datetime.utcnow() + timedelta(days=days)


def generate_signal_message(signal):
    """Format signal for Telegram/Email."""
    return f"""
*Trading Signal Alert*

Pair: {signal.pair}
Type: *{signal.signal_type}*
Entry Condition: {signal.entry_condition}
Take Profit: {signal.tp if signal.tp else 'N/A'}
Stop Loss: {signal.sl if signal.sl else 'N/A'}

Trade at your own risk.
    """


def validate_trading_pair(pair):
    """Validate trading pair format."""
    valid_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT', 'SOL/USDT']
    return pair in valid_pairs
