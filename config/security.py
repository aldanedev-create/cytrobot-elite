import os
from datetime import timedelta

class SecurityConfig:
    """Security configuration settings"""
    
    # Password hashing
    BCRYPT_ROUNDS = 12
    BCRYPT_LOG_ROUNDS = 12
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_LOGIN = "5 per minute"
    RATELIMIT_API = "60 per minute"
    
    # 2FA settings
    TWOFA_ISSUER_NAME = "CryptoBot"
    TWOFA_WINDOW = 1  # 1 step window for time drift
    
    # JWT settings (for API)
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', os.getenv('SECRET_KEY'))
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:5000', 'https://yourdomain.com']
    CORS_ALLOW_CREDENTIALS = True
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Frame-Options': 'DENY',
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://chart.googleapis.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https://chart.googleapis.com;"
    }
    
    # IP whitelist for admin (optional)
    ADMIN_IP_WHITELIST = []  # Empty means all IPs allowed
    
    # Suspicious activity thresholds
    BRUTE_FORCE_THRESHOLD = 5  # attempts
    BRUTE_FORCE_WINDOW = 15  # minutes
    SUSPICIOUS_ADMIN_ACTIONS = 10  # actions per 5 minutes
    ABNORMAL_TRADING_COUNT = 20  # trades per hour
    
    @classmethod
    def get_security_headers(cls):
        """Get security headers as dictionary"""
        return cls.SECURITY_HEADERS
    
    @classmethod
    def is_ip_allowed(cls, ip_address):
        """Check if IP is whitelisted for admin access"""
        if not cls.ADMIN_IP_WHITELIST:
            return True
        return ip_address in cls.ADMIN_IP_WHITELIST