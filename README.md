# 📚 Crypto Trading Bot System - Complete README

```markdown
# 🤖 Crypto Trading Bot System

A professional, production-ready cryptocurrency trading bot platform with automated signal generation, Telegram integration, role-based access control, SIEM security monitoring, and subscription management.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [User Guide](#user-guide)
- [Admin Guide](#admin-guide)
- [Security Features](#security-features)
- [Trading Engine](#trading-engine)
- [Telegram Bot Setup](#telegram-bot-setup)
- [Email Configuration](#email-configuration)
- [Troubleshooting](#troubleshooting)
- [Deployment](#deployment)
- [License](#license)

## 🚀 Overview

Crypto Trading Bot is a comprehensive automated trading signal platform that:

- **Analyzes** market data using technical indicators (RSI, EMA, MACD)
- **Generates** trading signals based on predefined strategies
- **Delivers** instant alerts via Telegram and Email
- **Manages** users with role-based access control (RBAC)
- **Monitors** security with built-in SIEM system
- **Tracks** all admin actions with complete audit logs

### System Capabilities

| Feature | Description |
|---------|-------------|
| **Manual Signals** | Admin creates signals, bot monitors and executes |
| **Auto Signals** | Bot generates signals using technical analysis |
| **Real-time Delivery** | Telegram alerts in < 1 second |
| **User Management** | Complete CRUD with role management |
| **Security** | 2FA, SIEM, audit logging, brute force protection |
| **Monetization** | Subscription plans with discount codes |

## ✨ Features

### 🔐 Authentication & Security
- ✅ User registration with email verification
- ✅ Login with 365-day persistent sessions
- ✅ Two-Factor Authentication (2FA) via Google Authenticator
- ✅ Password reset with email tokens
- ✅ Role-Based Access Control (RBAC)
- ✅ Session management with automatic timeout
- ✅ Brute force protection

### 📊 Trading Engine
- ✅ Real-time market data from Binance API
- ✅ Technical indicators: RSI, EMA, MACD
- ✅ Dual signal modes: Manual & Automated
- ✅ Conditional signal execution
- ✅ Stop Loss & Take Profit support
- ✅ Signal history tracking

### 🤖 Telegram Integration
- ✅ Instant signal delivery to Telegram
- ✅ Bot commands: /start, /help, /signals, /status
- ✅ Account linking via verification codes
- ✅ Inline keyboard buttons for easy navigation
- ✅ Group and individual notifications

### 👥 User Management
- ✅ User registration and profiles
- ✅ Subscription plans (Demo, Basic)
- ✅ Demo mode (5 days free)
- ✅ Payment processing integration
- ✅ Discount code system
- ✅ Email notifications

### 👑 Admin Panel
- ✅ Admin dashboard with statistics
- ✅ User management (block/unblock, role change)
- ✅ Signal management (create, delete, monitor)
- ✅ Trading pair management
- ✅ Payment overview
- ✅ Activity logs viewer
- ✅ SIEM security events monitoring

### 📈 SIEM Security System
- ✅ Real-time security monitoring
- ✅ Brute force detection
- ✅ Suspicious activity alerts
- ✅ Admin action logging
- ✅ IP address tracking
- ✅ Security event dashboard

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  HTML5   │  │  CSS3    │  │  JS      │  │ Bootstrap│       │
│  │  Jinja2  │  │  Custom  │  │  AJAX    │  │    5     │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER (Flask)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   Auth   │  │  Users   │  │ Trading  │  │  Admin   │       │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Payments │  │   Bot    │  │   Logs   │  │   SIEM   │       │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER (SQLite)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Users   │  │  Trades  │  │ Payments │  │   Logs   │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ Binance  │  │Telegram  │  │  Gmail   │  │ Finnhub  │       │
│  │   API    │  │   Bot    │  │  SMTP    │  │   API    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 💻 Installation

### Prerequisites

```bash
# System Requirements
- Python 3.8 or higher
- SQLite3 (built-in with Python)
- 1GB RAM minimum
- 500MB disk space
- Internet connection for API access
```

### Step 1: Clone or Create Project

```bash
# Create project directory
mkdir CryptoBotSystem
cd CryptoBotSystem

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

Create `requirements.txt`:

```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
python-dotenv==1.0.0
requests==2.31.0
python-telegram-bot==20.6
pandas==2.0.3
numpy==1.24.3
bcrypt==4.0.1
pyotp==2.9.0
email-validator==2.0.0
schedule==1.2.0
```

Install:

```bash
pip install -r requirements.txt
```

### Step 3: Create Project Structure

```bash
# Create all directories
mkdir -p config database auth users trading bot payments logs admin utils
mkdir -p templates templates/admin templates/includes
mkdir -p static/css static/js static/images
mkdir -p instance backups

# Create empty __init__.py files
touch config/__init__.py database/__init__.py auth/__init__.py
touch users/__init__.py trading/__init__.py bot/__init__.py
touch payments/__init__.py logs/__init__.py admin/__init__.py
touch utils/__init__.py
```

## ⚙️ Configuration

### Step 1: Environment Variables

Create `.env` file in root directory:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this-to-random-string
FLASK_ENV=production
FLASK_DEBUG=False

# Database
DATABASE_URL=sqlite:///crypto_bot.db

# Email Configuration (Gmail)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-specific-password

# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Binance API (Optional, for live data)
BINANCE_API_KEY=your-binance-api-key
BINANCE_API_SECRET=your-binance-api-secret

# Session Configuration
SESSION_COOKIE_DAYS=365
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### Step 2: Generate Secret Key

```python
# Run this in Python to generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 3: Gmail Setup for 2FA/Password Reset

1. Enable 2FA on your Google account
2. Generate App Password:
   - Go to Google Account → Security
   - App Passwords → Select "Mail" and "Other"
   - Copy the 16-character password
   - Use this in `EMAIL_PASSWORD`

## 🗄️ Database Setup

### Create Database

```bash
# Run the database creation script
python create_database.py
```

This will create:
- 10 tables with all relationships
- 35+ indexes for performance
- Default admin user
- Sample trading pairs
- Demo data

### Database Schema

```
Tables:
├── users                  # User accounts and profiles
├── trades                 # Trading signals
├── trading_pairs         # Supported trading pairs
├── subscriptions         # User subscriptions
├── payments              # Payment transactions
├── discount_codes        # Promotional codes
├── admin_logs            # Admin audit trail
├── security_events       # SIEM security events
├── signal_history        # Signal delivery records
└── password_reset_tokens # Password reset tokens
```

## 🚀 Running the Application

### Development Mode

```bash
# Set environment
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the application
python app.py
```

### Production Mode (using Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
```

### Using Waitress (Windows)

```bash
# Install waitress
pip install waitress

# Run with waitress
waitress-serve --port=5000 app:app
```

### Access the Application

```
Web Interface: http://localhost:5000
Default Admin: admin@cryptobot.com / Admin123!
```

## 📡 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Create new user account |
| `/login` | POST | Authenticate user |
| `/logout` | GET | Logout user |
| `/verify-2fa` | POST | Verify 2FA code |
| `/forgot-password` | POST | Request password reset |
| `/reset-password/<token>` | POST | Reset password |

### Trading Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/market-data/<pair>` | GET | Get live market data |
| `/api/check-signals` | GET | Check and execute signals |
| `/api/user/signals` | GET | Get user's signal history |
| `/signals` | GET | View all signals |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin` | GET | Admin dashboard |
| `/admin/users` | GET | User management |
| `/admin/users/<id>/block` | POST | Block user |
| `/admin/trades` | GET | Trade management |
| `/admin/trades/create` | POST | Create signal |
| `/admin/pairs` | GET | Pair management |
| `/admin/logs` | GET | View activity logs |

## 👤 User Guide

### Registration

1. Navigate to `http://localhost:5000/register`
2. Fill in username, email, and password
3. Click "Register"
4. Login with your credentials

### Setting Up 2FA

1. Go to Account Settings
2. Click "Enable 2FA"
3. Scan QR code with Google Authenticator
4. Enter verification code to confirm

### Connecting Telegram

1. Start a chat with your bot: `@YourBotUsername`
2. Send `/start`
3. Go to Account Settings → Get verification code
4. Send `/link YOUR_CODE` to the bot

### Subscribing to Plan

1. Go to Dashboard
2. Scroll to "Subscription Section"
3. Choose Demo (free 5 days) or Basic ($5/month)
4. Enter discount code (optional)
5. Complete payment

### Receiving Signals

- **Telegram**: Instant notifications when signals trigger
- **Email**: Optional email alerts
- **Dashboard**: View signal history

## 👑 Admin Guide

### Default Admin Access

```
URL: http://localhost:5000/login
Email: admin@cryptobot.com
Password: Admin123!
```

### Creating Trading Signals

1. Login as Admin
2. Go to Admin Panel → Manage Trades
3. Fill in:
   - Trading Pair (e.g., BTC/USDT)
   - Signal Type (BUY/SELL)
   - Entry Condition (e.g., "RSI < 30 AND EMA crossover")
   - Take Profit price
   - Stop Loss price
4. Click "Create Signal"

### Entry Condition Examples

```python
# Simple conditions
"RSI < 30"
"RSI > 70"
"EMA crossover"

# Complex conditions
"RSI < 30 AND EMA crossover AND MACD bullish"
"RSI > 70 AND bearish divergence"

# Price-based
"price > 65000 AND volume > 1000"
```

### Managing Users

1. Go to Admin Panel → Users
2. View all registered users
3. Block/Unblock users
4. Change user roles (Super Admin only)

### Viewing Security Logs

1. Go to Admin Panel → Security Events
2. View real-time security monitoring
3. Filter by severity (info/warning/critical)
4. Investigate suspicious activity

## 🔒 Security Features

### Two-Factor Authentication (2FA)

```python
# Users must set up 2FA in account settings
# Login flow:
1. Enter email/password
2. Verify 6-digit code from authenticator
3. Access granted
```

### SIEM Monitoring

```python
# Detects:
- Brute force attacks (5+ failed attempts)
- Suspicious admin activity (10+ actions in 5 min)
- Abnormal trading patterns (20+ trades/hour)
- API failures and system errors
```

### Audit Logging

```python
# Every admin action is logged:
- Who performed the action
- What action was taken
- When it happened
- IP address and user agent
```

### Password Security

```python
# Passwords are:
- Hashed using bcrypt (12 rounds)
- Never stored in plain text
- Minimum 8 characters
- Must contain uppercase, lowercase, numbers
```

## 🤖 Trading Engine

### Technical Indicators

#### RSI (Relative Strength Index)
```python
# Oversold: RSI < 30 → BUY signal
# Overbought: RSI > 70 → SELL signal
```

#### EMA (Exponential Moving Average)
```python
# Bullish: EMA 20 crosses above EMA 50 → BUY
# Bearish: EMA 20 crosses below EMA 50 → SELL
```

#### MACD (Moving Average Convergence Divergence)
```python
# Bullish: MACD line crosses above Signal line → BUY
# Bearish: MACD line crosses below Signal line → SELL
```

### Signal Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│ 1. Admin creates signal with conditions                 │
│    ↓                                                    │
│ 2. Bot fetches market data every 60 seconds            │
│    ↓                                                    │
│ 3. Calculates RSI, EMA, MACD                           │
│    ↓                                                    │
│ 4. Compares with signal conditions                     │
│    ↓                                                    │
│ 5. If conditions met → Execute signal                  │
│    ↓                                                    │
│ 6. Send to Telegram/Email                              │
│    ↓                                                    │
│ 7. Log to database                                     │
└─────────────────────────────────────────────────────────┘
```

## 🤖 Telegram Bot Setup

### Creating a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name (e.g., "Crypto Trading Bot")
4. Choose a username (must end with 'bot')
5. Copy the API token

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and menu |
| `/help` | Show all commands |
| `/link CODE` | Link Telegram to your account |
| `/signals` | Get latest trading signals |
| `/status` | Check subscription status |
| `/unlink` | Unlink Telegram account |

### Testing the Bot

```bash
# Send a test message via API
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" \
  -d "chat_id=<CHAT_ID>&text=Hello from CryptoBot!"
```

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication on Google Account
2. Generate App Password:
   - Google Account → Security → App Passwords
   - Select "Mail" and "Other"
   - Copy the 16-character password

### Email Templates

```python
# Password Reset Email
Subject: "Reset Your CryptoBot Password"
Body: Click the link to reset your password

# 2FA Code Email
Subject: "Your 2FA Verification Code"
Body: Your code is: XXXXXX

# Signal Alert Email
Subject: "New Trading Signal: BUY BTC/USDT"
Body: Entry: $65,000, TP: $67,000, SL: $63,000
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### Database Issues

```bash
# Database locked error
rm instance/crypto_bot.db
python create_database.py

# Foreign key constraint failed
PRAGMA foreign_keys = OFF;
# Run your operations
PRAGMA foreign_keys = ON;
```

#### Login Issues

```python
# Can't login after many attempts
# Check if user is blocked in database
UPDATE users SET is_blocked = 0 WHERE email = 'user@example.com';
```

#### Telegram Bot Not Working

```bash
# Check bot token
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe

# Check webhook (if using)
curl https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo
```

#### Email Sending Fails

```python
# Test SMTP connection
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'app-password')
```

#### Market Data Not Fetching

```python
# Check Binance API status
curl https://api.binance.com/api/v3/ping

# Test specific pair
curl https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT
```

### Debug Mode

```bash
# Enable debug mode for detailed logs
export FLASK_DEBUG=1
python app.py

# Check logs
tail -f logs/app.log
```

## 🚢 Deployment

### Deploy to Heroku

```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.9.0" > runtime.txt

# Deploy
heroku create crypto-bot-system
heroku config:set SECRET_KEY=your-secret-key
heroku config:set EMAIL_USER=your-email@gmail.com
heroku config:set TELEGRAM_BOT_TOKEN=your-token
git push heroku main
```

### Deploy to DigitalOcean (Docker)

```dockerfile
# Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Build and run
docker build -t crypto-bot .
docker run -d -p 5000:5000 --env-file .env crypto-bot
```

### Deploy to AWS EC2

```bash
# SSH into EC2
ssh -i key.pem ec2-user@your-instance

# Install dependencies
sudo yum install python3 git
git clone your-repo
cd CryptoBotSystem
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with supervisor
sudo pip install supervisor
echo_supervisord_conf > supervisord.conf
# Configure and run
supervisord -c supervisord.conf
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias /path/to/CryptoBotSystem/static;
    }
}
```

## 📊 Monitoring & Maintenance

### Backup Database

```bash
# Automatic backup script
#!/bin/bash
BACKUP_DIR="/backups"
DB_PATH="instance/crypto_bot.db"
DATE=$(date +%Y%m%d_%H%M%S)

sqlite3 $DB_PATH ".backup" "$BACKUP_DIR/crypto_bot_$DATE.db"
gzip "$BACKUP_DIR/crypto_bot_$DATE.db"

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

### Log Rotation

```python
# Add to app.py
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('logs/app.log', maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### Performance Monitoring

```sql
-- Check database size
SELECT page_count * page_size as size_bytes 
FROM pragma_page_count(), pragma_page_size();

-- Check index usage
SELECT name, sql FROM sqlite_master WHERE type='index';

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';
```

## 📈 Scaling Considerations

### For 1,000+ Users

```python
# Use PostgreSQL instead of SQLite
DATABASE_URL = postgresql://user:pass@localhost/crypto_bot

# Add Redis for caching
# Add Celery for background tasks
# Use multiple workers
gunicorn --workers 4 --threads 2 app:app
```

### For 10,000+ Users

```yaml
# Docker Compose with services:
services:
  web: gunicorn with 8 workers
  worker: celery for signal processing
  redis: message broker
  postgres: production database
  nginx: load balancer
```

## 🤝 Contributing

### Development Workflow

```bash
# Fork and clone
git clone https://github.com/yourusername/CryptoBotSystem.git
cd CryptoBotSystem

# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "Add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Code Standards

```python
# Follow PEP 8
# Use type hints
def get_user(user_id: int) -> User:
    return User.query.get(user_id)

# Write docstrings
def calculate_rsi(prices: list, period: int = 14) -> float:
    """Calculate Relative Strength Index
    
    Args:
        prices: List of price values
        period: RSI period (default 14)
    
    Returns:
        RSI value between 0-100
    """
    pass
```

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

**Trading cryptocurrencies involves substantial risk of loss and is not suitable for every investor. Past performance does not guarantee future results. This bot is for educational purposes. Use at your own risk.**

## 📞 Support

- Issues: GitHub Issues
- Email: support@cryptobot.com
- Telegram: @CryptoBotSupport

## 🙏 Acknowledgments

- Binance API for market data
- Python Telegram Bot library
- Flask ecosystem
- SQLAlchemy ORM

---

## 🎯 Quick Start Commands

```bash
# 1. Clone/Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your credentials

# 4. Database
python create_database.py

# 5. Run
python app.py

# 6. Access
# Open http://localhost:5000
# Login: admin@cryptobot.com / Admin123!
```

---

**Built with ❤️ using Python, Flask, and SQLite**
```

This README provides complete documentation for your Crypto Trading Bot System including installation, configuration, usage, and deployment instructions. Save this as `README.md` in your project root directory.
