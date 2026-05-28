import secrets
from datetime import datetime, timedelta


class TwoFAHandler:
    def __init__(self, db, User, ActivityLogger, Notifier):
        self.db = db
        self.User = User
        self.ActivityLogger = ActivityLogger
        self.Notifier = Notifier

    def generate_email_code(self):
        return f"{secrets.randbelow(1000000):06d}"

    def issue_email_code(self, user, session, purpose):
        code = self.generate_email_code()
        session[f'{purpose}_2fa_code'] = code
        session[f'{purpose}_2fa_expires'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        session[f'{purpose}_2fa_user_id'] = user.id
        sent = self.Notifier.send_2fa_code(user.email, code)
        return code if sent else None

    def verify_session_code(self, session, purpose, user, code):
        expected = session.get(f'{purpose}_2fa_code')
        expires = session.get(f'{purpose}_2fa_expires')
        user_id = session.get(f'{purpose}_2fa_user_id')

        if not expected or not expires or user_id != user.id:
            return False

        try:
            expires_at = datetime.fromisoformat(expires)
        except ValueError:
            return False

        return expires_at >= datetime.utcnow() and secrets.compare_digest(str(expected), str(code or '').strip())

    def clear_session_code(self, session, purpose):
        session.pop(f'{purpose}_2fa_code', None)
        session.pop(f'{purpose}_2fa_expires', None)
        session.pop(f'{purpose}_2fa_user_id', None)

    def verify_otp(self, user, code):
        return False

    def enable_2fa(self, user):
        user.twofa_secret = None
        user.twofa_enabled = True
        self.db.session.commit()
        self.ActivityLogger.log_activity(user.id, 'ENABLE_2FA', 'Email 2FA enabled for account', None)
        return True

    def disable_2fa(self, user):
        user.twofa_secret = None
        user.twofa_enabled = False
        self.db.session.commit()
        self.ActivityLogger.log_activity(user.id, 'DISABLE_2FA', 'Email 2FA disabled for account', None)
