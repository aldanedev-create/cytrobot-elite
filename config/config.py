import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///crypto_bot.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session Config
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=int(os.getenv('SESSION_COOKIE_DAYS', 365)))
    
    # Email Config
    MAIL_SERVER = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Trading Config
    BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
    BINANCE_API_SECRET = os.getenv('BINANCE_API_SECRET')
    
    # Telegram Config
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # App Config
    DEMO_DAYS = 5
    BASIC_PLAN_PRICE = 5
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', os.getenv('EMAIL_USER'))
