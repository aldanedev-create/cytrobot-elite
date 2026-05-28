-- =====================================================
-- CRYPTO TRADING BOT DATABASE SCHEMA
-- SQLite Version
-- =====================================================

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- =====================================================
-- 1. USERS TABLE (Core authentication & profiles)
-- =====================================================

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(200) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    subscription_status VARCHAR(20) DEFAULT 'inactive',
    is_active BOOLEAN DEFAULT 1,
    is_blocked BOOLEAN DEFAULT 0,
    telegram_chat_id VARCHAR(50),
    twofa_secret VARCHAR(50),
    twofa_enabled BOOLEAN DEFAULT 0,
    demo_expiry DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    
    -- Constraints
    CHECK (role IN ('super_admin', 'admin', 'user')),
    CHECK (subscription_status IN ('active', 'inactive', 'demo')),
    CHECK (is_active IN (0, 1)),
    CHECK (is_blocked IN (0, 1)),
    CHECK (twofa_enabled IN (0, 1))
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_subscription_status ON users(subscription_status);
CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_blocked ON users(is_blocked);
CREATE INDEX idx_users_telegram_chat_id ON users(telegram_chat_id);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login);

-- Composite indexes
CREATE INDEX idx_users_role_status ON users(role, subscription_status);
CREATE INDEX idx_users_active_blocked ON users(is_active, is_blocked);


-- =====================================================
-- 2. TRADES TABLE (Signals created by admins/bot)
-- =====================================================

DROP TABLE IF EXISTS trades;
CREATE TABLE trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair VARCHAR(20) NOT NULL,
    signal_type VARCHAR(10) NOT NULL,
    entry_condition TEXT NOT NULL,
    tp DECIMAL(20, 8),
    sl DECIMAL(20, 8),
    entry_price DECIMAL(20, 8),
    status VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    executed_at DATETIME,
    
    -- Foreign keys
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Constraints
    CHECK (signal_type IN ('BUY', 'SELL', 'NONE')),
    CHECK (status IN ('pending', 'executed', 'cancelled', 'expired')),
    CHECK (tp > 0 OR tp IS NULL),
    CHECK (sl > 0 OR sl IS NULL),
    CHECK (entry_price >= 0 OR entry_price IS NULL)
);

-- Indexes for trades table
CREATE INDEX idx_trades_pair ON trades(pair);
CREATE INDEX idx_trades_signal_type ON trades(signal_type);
CREATE INDEX idx_trades_status ON trades(status);
CREATE INDEX idx_trades_created_by ON trades(created_by);
CREATE INDEX idx_trades_created_at ON trades(created_at);
CREATE INDEX idx_trades_executed_at ON trades(executed_at);
CREATE INDEX idx_trades_entry_price ON trades(entry_price);

-- Composite indexes
CREATE INDEX idx_trades_pair_status ON trades(pair, status);
CREATE INDEX idx_trades_type_status ON trades(signal_type, status);
CREATE INDEX idx_trades_created_status ON trades(created_by, status);
CREATE INDEX idx_trades_date_status ON trades(created_at, status);


-- =====================================================
-- 3. TRADING_PAIRS TABLE (Supported trading pairs)
-- =====================================================

DROP TABLE IF EXISTS trading_pairs;
CREATE TABLE trading_pairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pair_name VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT 1,
    min_quantity DECIMAL(20, 8) DEFAULT 0.001,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (is_active IN (0, 1)),
    CHECK (min_quantity >= 0)
);

-- Indexes for trading_pairs table
CREATE INDEX idx_trading_pairs_name ON trading_pairs(pair_name);
CREATE INDEX idx_trading_pairs_active ON trading_pairs(is_active);
CREATE INDEX idx_trading_pairs_created ON trading_pairs(created_at);


-- =====================================================
-- 4. SUBSCRIPTIONS TABLE (User subscription plans)
-- =====================================================

DROP TABLE IF EXISTS subscriptions;
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan VARCHAR(20) NOT NULL,
    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_date DATETIME NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (plan IN ('basic', 'demo', 'premium')),
    CHECK (is_active IN (0, 1)),
    CHECK (end_date > start_date)
);

-- Indexes for subscriptions table
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_plan ON subscriptions(plan);
CREATE INDEX idx_subscriptions_is_active ON subscriptions(is_active);
CREATE INDEX idx_subscriptions_start_date ON subscriptions(start_date);
CREATE INDEX idx_subscriptions_end_date ON subscriptions(end_date);

-- Composite indexes
CREATE INDEX idx_subscriptions_user_active ON subscriptions(user_id, is_active);
CREATE INDEX idx_subscriptions_plan_status ON subscriptions(plan, is_active);
CREATE INDEX idx_subscriptions_date_range ON subscriptions(start_date, end_date);


-- =====================================================
-- 5. PAYMENTS TABLE (Transaction records)
-- =====================================================

DROP TABLE IF EXISTS payments;
CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    discount_code VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (amount >= 0),
    CHECK (currency IN ('USD', 'EUR', 'GBP', 'USDT')),
    CHECK (status IN ('pending', 'completed', 'failed', 'refunded'))
);

-- Indexes for payments table
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_transaction_id ON payments(transaction_id);
CREATE INDEX idx_payments_discount_code ON payments(discount_code);
CREATE INDEX idx_payments_created_at ON payments(created_at);
CREATE INDEX idx_payments_amount ON payments(amount);

-- Composite indexes
CREATE INDEX idx_payments_user_status ON payments(user_id, status);
CREATE INDEX idx_payments_date_status ON payments(created_at, status);
CREATE INDEX idx_payments_user_date ON payments(user_id, created_at);


-- =====================================================
-- 6. DISCOUNT_CODES TABLE (Promotional codes)
-- =====================================================

DROP TABLE IF EXISTS discount_codes;
CREATE TABLE discount_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) NOT NULL UNIQUE,
    discount_percent INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    expires_at DATETIME,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    
    CHECK (discount_percent BETWEEN 0 AND 100),
    CHECK (is_active IN (0, 1))
);

-- Indexes for discount_codes table
CREATE INDEX idx_discount_codes_code ON discount_codes(code);
CREATE INDEX idx_discount_codes_active ON discount_codes(is_active);
CREATE INDEX idx_discount_codes_expires_at ON discount_codes(expires_at);
CREATE INDEX idx_discount_codes_created_by ON discount_codes(created_by);

-- Composite indexes
CREATE INDEX idx_discount_codes_active_expires ON discount_codes(is_active, expires_at);


-- =====================================================
-- 7. ADMIN_LOGS TABLE (Audit trail for admin actions)
-- =====================================================

DROP TABLE IF EXISTS admin_logs;
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(200),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (action_type IN (
        'LOGIN', 'LOGOUT', 'REGISTER', 'CREATE_SIGNAL', 'DELETE_SIGNAL', 
        'UPDATE_SIGNAL', 'CANCEL_SIGNAL', 'BLOCK_USER', 'UNBLOCK_USER', 
        'CHANGE_ROLE', 'DELETE_USER', 'ADD_PAIR', 'REMOVE_PAIR', 'TOGGLE_PAIR',
        'CREATE_DISCOUNT', 'DELETE_DISCOUNT', 'COMPLETE_PAYMENT', 'REFUND_PAYMENT',
        'UPDATE_PROFILE', 'CHANGE_PASSWORD', 'ENABLE_2FA', 'DISABLE_2FA'
    ))
);

-- Indexes for admin_logs table
CREATE INDEX idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX idx_admin_logs_action_type ON admin_logs(action_type);
CREATE INDEX idx_admin_logs_timestamp ON admin_logs(timestamp);
CREATE INDEX idx_admin_logs_ip_address ON admin_logs(ip_address);

-- Composite indexes
CREATE INDEX idx_admin_logs_admin_action ON admin_logs(admin_id, action_type);
CREATE INDEX idx_admin_logs_time_action ON admin_logs(timestamp, action_type);
CREATE INDEX idx_admin_logs_admin_time ON admin_logs(admin_id, timestamp);


-- =====================================================
-- 8. SECURITY_EVENTS TABLE (SIEM monitoring)
-- =====================================================

DROP TABLE IF EXISTS security_events;
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    CHECK (severity IN ('info', 'warning', 'critical')),
    CHECK (resolved IN (0, 1)),
    CHECK (event_type IN (
        'FAILED_LOGIN', 'SUCCESSFUL_LOGIN', 'BLOCKED_LOGIN', 'BRUTE_FORCE',
        'SUSPICIOUS_ADMIN_ACTIVITY', 'ABNORMAL_TRADING_ACTIVITY',
        'SYSTEM_ERROR', 'API_FAILURE', 'TELEGRAM_ERROR', 'PAYMENT_FAILURE',
        'BRUTE_FORCE_DETECTED', 'SUSPICIOUS_ACTIVITY'
    ))
);

-- Indexes for security_events table
CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX idx_security_events_ip_address ON security_events(ip_address);
CREATE INDEX idx_security_events_resolved ON security_events(resolved);

-- Composite indexes
CREATE INDEX idx_security_events_severity_time ON security_events(severity, timestamp);
CREATE INDEX idx_security_events_user_severity ON security_events(user_id, severity);
CREATE INDEX idx_security_unresolved ON security_events(resolved, severity);


-- =====================================================
-- 9. SIGNAL_HISTORY TABLE (User signal delivery records)
-- =====================================================

DROP TABLE IF EXISTS signal_history;
CREATE TABLE signal_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trade_id INTEGER NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivered_via VARCHAR(20) DEFAULT 'telegram',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE CASCADE,
    
    CHECK (delivered_via IN ('telegram', 'email', 'both'))
);

-- Indexes for signal_history table
CREATE INDEX idx_signal_history_user_id ON signal_history(user_id);
CREATE INDEX idx_signal_history_trade_id ON signal_history(trade_id);
CREATE INDEX idx_signal_history_sent_at ON signal_history(sent_at);
CREATE INDEX idx_signal_history_delivered_via ON signal_history(delivered_via);

-- Composite indexes
CREATE INDEX idx_signal_history_user_trade ON signal_history(user_id, trade_id);
CREATE INDEX idx_signal_history_user_time ON signal_history(user_id, sent_at);


-- =====================================================
-- 10. PASSWORD_RESET_TOKENS TABLE
-- =====================================================

DROP TABLE IF EXISTS password_reset_tokens;
CREATE TABLE password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token VARCHAR(100) NOT NULL UNIQUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (used IN (0, 1)),
    CHECK (expires_at > created_at)
);

-- Indexes for password_reset_tokens
CREATE INDEX idx_password_reset_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_user_id ON password_reset_tokens(user_id);
CREATE INDEX idx_password_reset_expires_at ON password_reset_tokens(expires_at);
CREATE INDEX idx_password_reset_used ON password_reset_tokens(used);

-- Composite indexes
CREATE INDEX idx_password_reset_user_used ON password_reset_tokens(user_id, used);


-- =====================================================
-- 11. API_KEYS TABLE (For exchange API integration)
-- =====================================================

DROP TABLE IF EXISTS api_keys;
CREATE TABLE api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exchange VARCHAR(50) NOT NULL,
    api_key VARCHAR(200) NOT NULL,
    api_secret VARCHAR(200) NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    permissions VARCHAR(100) DEFAULT 'read',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (exchange IN ('binance', 'coinbase', 'kraken', 'bybit')),
    CHECK (is_active IN (0, 1)),
    CHECK (permissions IN ('read', 'trade', 'withdraw', 'read,trade'))
);

-- Indexes for api_keys
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_exchange ON api_keys(exchange);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);
CREATE INDEX idx_api_keys_user_exchange ON api_keys(user_id, exchange);


-- =====================================================
-- 12. NOTIFICATION_SETTINGS TABLE
-- =====================================================

DROP TABLE IF EXISTS notification_settings;
CREATE TABLE notification_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    telegram_enabled BOOLEAN DEFAULT 1,
    email_enabled BOOLEAN DEFAULT 1,
    signal_alerts BOOLEAN DEFAULT 1,
    price_alerts BOOLEAN DEFAULT 0,
    system_alerts BOOLEAN DEFAULT 1,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    CHECK (telegram_enabled IN (0, 1)),
    CHECK (email_enabled IN (0, 1)),
    CHECK (signal_alerts IN (0, 1)),
    CHECK (price_alerts IN (0, 1)),
    CHECK (system_alerts IN (0, 1))
);

-- Indexes for notification_settings
CREATE INDEX idx_notification_settings_user ON notification_settings(user_id);


-- =====================================================
-- SAMPLE DATA (For testing)
-- =====================================================

-- Insert default Super Admin
INSERT OR REPLACE INTO users (
    email, username, password_hash, role, subscription_status, 
    is_active, is_blocked, twofa_enabled, created_at
) VALUES (
    'aldanehutchinson5@gmail.com', 
    'superadmin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYjFYKHxQy/K',  -- Admin123!
    'super_admin', 
    'active',
    1, 0, 0, 
    CURRENT_TIMESTAMP
);

-- Insert demo user
INSERT OR REPLACE INTO users (
    email, username, password_hash, role, subscription_status,
    is_active, is_blocked, demo_expiry, created_at
) VALUES (
    'demo@cryptobot.com',
    'demouser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYjFYKHxQy/K',  -- Admin123!
    'user',
    'demo',
    1, 0,
    datetime('now', '+5 days'),
    CURRENT_TIMESTAMP
);

-- Insert regular user
INSERT OR REPLACE INTO users (
    email, username, password_hash, role, subscription_status,
    is_active, is_blocked, created_at
) VALUES (
    'user@cryptobot.com',
    'testuser',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.VTtYjFYKHxQy/K',  -- Admin123!
    'user',
    'inactive',
    1, 0,
    CURRENT_TIMESTAMP
);

-- Insert trading pairs
INSERT OR REPLACE INTO trading_pairs (pair_name, is_active, min_quantity) VALUES
    ('BTC/USDT', 1, 0.001),
    ('ETH/USDT', 1, 0.01),
    ('BNB/USDT', 1, 0.01),
    ('XRP/USDT', 1, 10),
    ('ADA/USDT', 1, 50),
    ('DOGE/USDT', 1, 100),
    ('SOL/USDT', 1, 0.1),
    ('MATIC/USDT', 1, 50),
    ('DOT/USDT', 1, 5),
    ('AVAX/USDT', 0, 0.1);  -- Inactive pair

-- Insert sample trades/signals
INSERT OR REPLACE INTO trades (
    pair, signal_type, entry_condition, tp, sl, status, created_by, created_at
) VALUES
    ('BTC/USDT', 'BUY', 'RSI < 30 AND EMA crossover', 70000, 63000, 'executed', 1, datetime('now', '-2 days')),
    ('ETH/USDT', 'BUY', 'MACD bullish and RSI < 40', 4000, 3500, 'pending', 1, datetime('now', '-1 day')),
    ('BNB/USDT', 'SELL', 'RSI > 70 and bearish divergence', 600, 650, 'pending', 1, datetime('now', '-12 hours')),
    ('SOL/USDT', 'BUY', 'Support bounce with volume', 150, 120, 'executed', 1, datetime('now', '-3 days')),
    ('XRP/USDT', 'SELL', 'Resistance rejection', 0.8, 0.85, 'cancelled', 1, datetime('now', '-5 days'));

-- Insert sample subscriptions
INSERT OR REPLACE INTO subscriptions (user_id, plan, start_date, end_date, is_active) VALUES
    (2, 'demo', datetime('now', '-2 days'), datetime('now', '+3 days'), 1),
    (1, 'basic', datetime('now', '-30 days'), datetime('now', '+30 days'), 1);

-- Insert sample payments
INSERT OR REPLACE INTO payments (user_id, amount, currency, status, transaction_id, created_at) VALUES
    (1, 5.00, 'USD', 'completed', 'TXN_' || hex(randomblob(8)), datetime('now', '-25 days')),
    (2, 0.00, 'USD', 'completed', 'TXN_DEMO_' || hex(randomblob(4)), datetime('now', '-2 days'));

-- Insert sample discount code
INSERT OR REPLACE INTO discount_codes (code, discount_percent, is_active, expires_at, created_by) VALUES
    ('WELCOME20', 20, 1, datetime('now', '+30 days'), 1),
    ('FIRSTMONTH', 50, 1, datetime('now', '+60 days'), 1),
    ('FLASHSALE', 30, 0, datetime('now', '-5 days'), 1);  -- Expired

-- Insert sample admin logs
INSERT OR REPLACE INTO admin_logs (admin_id, action_type, description, ip_address, timestamp) VALUES
    (1, 'LOGIN', 'Admin logged in successfully', '192.168.1.1', datetime('now', '-2 days')),
    (1, 'CREATE_SIGNAL', 'Created BUY signal for BTC/USDT', '192.168.1.1', datetime('now', '-2 days')),
    (1, 'CREATE_SIGNAL', 'Created BUY signal for ETH/USDT', '192.168.1.1', datetime('now', '-1 day')),
    (1, 'ADD_PAIR', 'Added trading pair SOL/USDT', '192.168.1.1', datetime('now', '-3 days'));

-- Insert sample security events
INSERT OR REPLACE INTO security_events (event_type, severity, description, ip_address, timestamp, resolved) VALUES
    ('SUCCESSFUL_LOGIN', 'info', 'User logged in successfully', '192.168.1.100', datetime('now', '-1 day'), 1),
    ('FAILED_LOGIN', 'warning', 'Failed login attempt for user@cryptobot.com', '203.0.113.5', datetime('now', '-12 hours'), 1),
    ('BRUTE_FORCE_DETECTED', 'critical', 'Multiple failed login attempts detected', '198.51.100.10', datetime('now', '-6 hours'), 0),
    ('API_FAILURE', 'warning', 'Binance API timeout', NULL, datetime('now', '-2 hours'), 0);

-- Insert sample signal history
INSERT OR REPLACE INTO signal_history (user_id, trade_id, sent_at, delivered_via) VALUES
    (2, 1, datetime('now', '-2 days'), 'telegram'),
    (2, 2, datetime('now', '-1 day'), 'telegram'),
    (1, 1, datetime('now', '-2 days'), 'email'),
    (2, 4, datetime('now', '-3 days'), 'telegram');

-- Insert notification settings
INSERT OR REPLACE INTO notification_settings (user_id, telegram_enabled, email_enabled, signal_alerts) VALUES
    (1, 1, 1, 1),
    (2, 1, 1, 1),
    (3, 0, 1, 1);

-- =====================================================
-- HELPER VIEWS (For reporting)
-- =====================================================

-- View: Active users with their subscription status
DROP VIEW IF EXISTS v_active_users;
CREATE VIEW v_active_users AS
SELECT 
    u.id,
    u.email,
    u.username,
    u.role,
    u.subscription_status,
    s.plan,
    s.end_date as subscription_end,
    CASE 
        WHEN u.subscription_status = 'active' AND s.end_date > CURRENT_TIMESTAMP THEN 'Valid'
        WHEN u.subscription_status = 'demo' AND u.demo_expiry > CURRENT_TIMESTAMP THEN 'Demo Valid'
        ELSE 'Expired'
    END as access_status
FROM users u
LEFT JOIN subscriptions s ON u.id = s.user_id AND s.is_active = 1
WHERE u.is_active = 1 AND u.is_blocked = 0;

-- View: Daily revenue report
DROP VIEW IF EXISTS v_daily_revenue;
CREATE VIEW v_daily_revenue AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    currency
FROM payments
WHERE status = 'completed'
GROUP BY DATE(created_at), currency
ORDER BY date DESC;

-- View: Signal performance statistics
DROP VIEW IF EXISTS v_signal_performance;
CREATE VIEW v_signal_performance AS
SELECT 
    pair,
    signal_type,
    COUNT(*) as total_signals,
    SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
    ROUND(100.0 * SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) / COUNT(*), 2) as execution_rate
FROM trades
GROUP BY pair, signal_type;

-- View: Admin activity summary
DROP VIEW IF EXISTS v_admin_activity;
CREATE VIEW v_admin_activity AS
SELECT 
    u.username as admin_name,
    al.action_type,
    COUNT(*) as action_count,
    DATE(al.timestamp) as date
FROM admin_logs al
JOIN users u ON al.admin_id = u.id
GROUP BY u.id, al.action_type, DATE(al.timestamp)
ORDER BY date DESC;

-- =====================================================
-- STORED PROCEDURES (Using SQLite triggers)
-- =====================================================

-- Trigger: Auto-update user subscription_status when subscription expires
DROP TRIGGER IF EXISTS trg_update_subscription_status;
CREATE TRIGGER trg_update_subscription_status
AFTER UPDATE ON subscriptions
BEGIN
    UPDATE users 
    SET subscription_status = 'inactive'
    WHERE id = NEW.user_id 
    AND NEW.is_active = 0;
END;

-- Trigger: Log all user status changes
DROP TRIGGER IF EXISTS trg_log_user_status_change;
CREATE TRIGGER trg_log_user_status_change
AFTER UPDATE OF is_blocked, role ON users
BEGIN
    INSERT INTO admin_logs (admin_id, action_type, description, timestamp)
    VALUES (
        NEW.id,
        CASE 
            WHEN NEW.is_blocked != OLD.is_blocked AND NEW.is_blocked = 1 THEN 'BLOCK_USER'
            WHEN NEW.is_blocked != OLD.is_blocked AND NEW.is_blocked = 0 THEN 'UNBLOCK_USER'
            WHEN NEW.role != OLD.role THEN 'CHANGE_ROLE'
        END,
        'User ' || NEW.email || ': ' || 
        CASE 
            WHEN NEW.is_blocked != OLD.is_blocked THEN 'blocked status changed to ' || NEW.is_blocked
            WHEN NEW.role != OLD.role THEN 'role changed from ' || OLD.role || ' to ' || NEW.role
        END,
        CURRENT_TIMESTAMP
    );
END;

-- =====================================================
-- ANALYTICS QUERIES
-- =====================================================

-- Query 1: Get user count by role and subscription status
SELECT 
    role,
    subscription_status,
    COUNT(*) as user_count
FROM users
GROUP BY role, subscription_status
ORDER BY role, subscription_status;

-- Query 2: Monthly revenue trend
SELECT 
    strftime('%Y-%m', created_at) as month,
    COUNT(*) as payment_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_payment
FROM payments
WHERE status = 'completed'
GROUP BY strftime('%Y-%m', created_at)
ORDER BY month DESC;

-- Query 3: Most active trading pairs
SELECT 
    pair,
    COUNT(*) as signal_count,
    COUNT(DISTINCT created_by) as admin_count
FROM trades
WHERE created_at >= datetime('now', '-30 days')
GROUP BY pair
ORDER BY signal_count DESC
LIMIT 10;

-- Query 4: Security event summary
SELECT 
    severity,
    event_type,
    COUNT(*) as event_count,
    COUNT(DISTINCT ip_address) as unique_ips
FROM security_events
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY severity, event_type
ORDER BY event_count DESC;

-- Query 5: User engagement (signals received per user)
SELECT 
    u.username,
    u.role,
    COUNT(sh.id) as signals_received,
    COUNT(DISTINCT sh.trade_id) as unique_signals
FROM users u
LEFT JOIN signal_history sh ON u.id = sh.user_id
GROUP BY u.id
ORDER BY signals_received DESC;

-- =====================================================
-- MAINTENANCE QUERIES
-- =====================================================

-- Clean up expired demo users (set to inactive)
UPDATE users 
SET subscription_status = 'inactive'
WHERE subscription_status = 'demo' 
AND demo_expiry < CURRENT_TIMESTAMP;

-- Clean up expired password reset tokens
DELETE FROM password_reset_tokens 
WHERE expires_at < CURRENT_TIMESTAMP;

-- Archive old logs (older than 90 days)
-- CREATE TABLE admin_logs_archive AS SELECT * FROM admin_logs WHERE timestamp < datetime('now', '-90 days');
-- DELETE FROM admin_logs WHERE timestamp < datetime('now', '-90 days');

-- Database optimization
PRAGMA optimize;
PRAGMA integrity_check;
PRAGMA foreign_key_check;

-- Show database size
SELECT 
    page_count * page_size as size_bytes,
    (page_count * page_size) / 1024.0 / 1024.0 as size_mb
FROM pragma_page_count(), pragma_page_size();

-- =====================================================
-- END OF DATABASE SCHEMA
-- =====================================================