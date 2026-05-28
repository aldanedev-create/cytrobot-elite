import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


class Notifier:
    def __init__(self, config):
        self.config = config
        self.telegram_token = config.get('TELEGRAM_BOT_TOKEN')

    def send_telegram_signal(self, chat_id, message, trade=None):
        if not self.telegram_token:
            return False

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"

        formatted_message = f"""
*NEW TRADING SIGNAL*

*Pair:* {trade.pair if trade else 'N/A'}
*Type:* `{trade.signal_type if trade else 'N/A'}`
*Entry:* {trade.entry_condition if trade else 'N/A'}
*Take Profit:* {trade.tp if trade and trade.tp else 'N/A'}
*Stop Loss:* {trade.sl if trade and trade.sl else 'N/A'}

*Risk Management:* Use proper position sizing.
        """

        payload = {
            'chat_id': chat_id,
            'text': formatted_message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {str(e)}")
            return False

    def send_telegram_alert(self, chat_id, message):
        if not self.telegram_token:
            return False

        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram error: {str(e)}")
            return False

    def send_email(self, to_email, subject, body):
        """Send email via SMTP when credentials are configured."""
        if not self.config.get('MAIL_USERNAME') or not self.config.get('MAIL_PASSWORD'):
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get('MAIL_USERNAME')
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.config.get('MAIL_SERVER'), self.config.get('MAIL_PORT'), timeout=15)
            server.starttls()
            server.login(self.config.get('MAIL_USERNAME'), self.config.get('MAIL_PASSWORD'))
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False

    def send_email_signal(self, to_email, trade):
        subject = f"New Trading Signal: {trade.signal_type} {trade.pair}"
        body = f"""
        <html>
        <body>
            <h2>New Trading Signal Alert</h2>
            <p><strong>Pair:</strong> {trade.pair}</p>
            <p><strong>Type:</strong> {trade.signal_type}</p>
            <p><strong>Entry Condition:</strong> {trade.entry_condition}</p>
            <p><strong>Take Profit:</strong> {trade.tp if trade.tp else 'N/A'}</p>
            <p><strong>Stop Loss:</strong> {trade.sl if trade.sl else 'N/A'}</p>
            <hr>
            <p><small>This is an automated message from CryptoBot. Trade at your own risk.</small></p>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body)

    def send_2fa_code(self, to_email, code):
        subject = "Your Gmail 2FA Verification Code"
        body = f"""
        <html>
        <body>
            <h2>Gmail Two-Factor Authentication Code</h2>
            <p>Your verification code is: <strong>{code}</strong></p>
            <p>This code will expire soon. No QR code or authenticator app is required.</p>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body)

    def send_contact_message(self, to_email, name, reply_to, audience, subject, message):
        body = f"""
        <html>
        <body>
            <h2>New Contact Message</h2>
            <p><strong>From:</strong> {name} ({reply_to})</p>
            <p><strong>Audience:</strong> {audience}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <hr>
            <p>{message}</p>
        </body>
        </html>
        """
        return self.send_email(to_email, f"Contact: {subject}", body)

    def send_password_reset_email(self, to_email, reset_link):
        subject = "Password Reset Request"
        body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">{reset_link}</a>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this, please ignore this email.</p>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, body)
