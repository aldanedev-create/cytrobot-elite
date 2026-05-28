import os
from uuid import uuid4

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import secrets

from config.config import Config
from database.db import db, login_manager
from database.models import User, Trade, TradingPair, Subscription, Payment, DiscountCode, AdminLog, SecurityEvent, SignalHistory, PasswordResetToken, RolePermission, Classroom, ClassroomMaterial, ContactMessage
from auth.login import LoginHandler
from auth.register import RegisterHandler
from auth.twofa import TwoFAHandler
from auth.middleware import role_required
from users.subscription import SubscriptionHandler
from trading.trading_engine import TradingEngine
from trading.signals import SignalManager
from trading.pairs import PairManager
from bot.notifier import Notifier
from logs.siem import SIEM
from admin.manage_users import UserManager
from admin.manage_trades import TradeManager
from admin.manage_pairs import PairManager as AdminPairManager
from logs.activity_logger import ActivityLogger
from utils.helpers import init_default_admin
from support.support_routes import register_support_routes

app = Flask(__name__)
app.config.from_object(Config)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

@app.context_processor
def inject_template_globals():
    return {'current_year': datetime.utcnow().year}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize handlers
activity_logger = ActivityLogger(db, AdminLog)
notifier = Notifier(app.config)

login_handler = LoginHandler(db, SecurityEvent, activity_logger)
register_handler = RegisterHandler(db, User, activity_logger)
twofa_handler = TwoFAHandler(db, User, activity_logger, notifier)
subscription_handler = SubscriptionHandler(db, User, Subscription, Payment)
signal_manager = SignalManager(db, Trade, notifier, activity_logger)
pair_manager = PairManager(db, TradingPair)
trading_engine = TradingEngine(db, Trade, signal_manager, activity_logger, SecurityEvent)
user_manager = UserManager(db, User, AdminLog, activity_logger)
trade_manager = TradeManager(db, Trade, activity_logger)
siem = SIEM(db, SecurityEvent, activity_logger)
register_support_routes(app, db, activity_logger)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        success, result = register_handler.register_user(email, username, password, confirm_password, request.remote_addr)
        if success:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash(result, 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        success, result = login_handler.authenticate(email, password, request.remote_addr, request.user_agent.string)
        
        if success:
            user = result
            if user.twofa_enabled:
                session['2fa_user_id'] = user.id
                if twofa_handler.issue_email_code(user, session, 'login'):
                    flash('Please enter the Gmail 2FA code sent to your email.', 'info')
                    return redirect(url_for('verify_2fa'))

                flash('Gmail 2FA code could not be sent. Check SMTP settings.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash(result, 'danger')
    
    return render_template('login.html')

@app.route('/verify-2fa', methods=['GET', 'POST'])
def verify_2fa():
    if '2fa_user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['2fa_user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        if twofa_handler.verify_session_code(session, 'login', user, code):
            login_user(user, remember=True)
            session.pop('2fa_user_id', None)
            twofa_handler.clear_session_code(session, 'login')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid 2FA code', 'danger')
    
    return render_template('verify_2fa.html')

@app.route('/logout')
@login_required
def logout():
    activity_logger.log_activity(current_user.id, 'LOGOUT', f'User logged out', request.remote_addr)
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_blocked:
        logout_user()
        flash('Your account has been blocked. Contact support.', 'danger')
        return redirect(url_for('login'))
    
    # Get user's signals
    signals = Trade.query.filter_by(status='pending').order_by(Trade.created_at.desc()).limit(50).all()
    
    # Get trading pairs
    pairs = TradingPair.query.filter_by(is_active=True).all()
    
    # Get user's subscription info
    subscription = Subscription.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    # Get recent signals for user
    recent_signals = SignalHistory.query.filter_by(user_id=current_user.id).order_by(SignalHistory.sent_at.desc()).limit(20).all()
    
    return render_template('dashboard.html', 
                         signals=signals, 
                         pairs=pairs, 
                         subscription=subscription,
                         recent_signals=recent_signals)

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            username = request.form.get('username')
            email = request.form.get('email')
            telegram_id = request.form.get('telegram_id')
            
            if username:
                current_user.username = username
            if email:
                current_user.email = email
            if telegram_id:
                current_user.telegram_chat_id = telegram_id
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
        
        elif action == 'change_password':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'danger')
            elif len(new_password) < 8:
                flash('Password must be at least 8 characters', 'danger')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password changed successfully', 'success')
        
        elif action == 'toggle_2fa':
            if current_user.twofa_enabled:
                twofa_handler.disable_2fa(current_user)
                flash('2FA disabled', 'warning')
            else:
                if twofa_handler.issue_email_code(current_user, session, 'enable'):
                    return render_template('account.html', user=current_user, show_email_2fa=True)
                flash('Gmail 2FA code could not be sent. Check SMTP settings.', 'danger')
    
    return render_template('account.html', user=current_user)

@app.route('/enable-2fa', methods=['POST'])
@login_required
def enable_2fa():
    code = request.form.get('code')

    if twofa_handler.verify_session_code(session, 'enable', current_user, code):
        twofa_handler.enable_2fa(current_user)
        twofa_handler.clear_session_code(session, 'enable')
        flash('2FA enabled successfully', 'success')
    else:
        flash('Invalid verification code', 'danger')
    
    return redirect(url_for('account'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            db.session.add(reset_token)
            db.session.commit()
            
            # Send email
            notifier = Notifier(app.config)
            reset_link = url_for('reset_password', token=token, _external=True)
            notifier.send_password_reset_email(user.email, reset_link)
            
        flash('If an account exists for that email, a reset link has been sent.', 'success')
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token or reset_token.expires_at < datetime.utcnow():
        flash('Invalid or expired reset token', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
        else:
            user = User.query.get(reset_token.user_id)
            user.set_password(password)
            reset_token.used = True
            db.session.commit()
            
            flash('Password reset successful! Please login', 'success')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html')

@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    plan = request.form.get('plan')
    discount_code = request.form.get('discount_code')

    if plan == 'demo':
        success, message = subscription_handler.create_demo(current_user.id)
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('dashboard'))

    if plan != 'basic':
        flash('Please choose a valid plan.', 'danger')
        return redirect(url_for('dashboard'))
    
    success, result = subscription_handler.create_subscription(current_user.id, plan, discount_code)
    
    if success:
        flash(result['message'], 'success')
        return redirect(url_for('payment_checkout', transaction_id=result['payment'].transaction_id))
    else:
        flash(result, 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/payment/checkout/<transaction_id>')
@login_required
def payment_checkout(transaction_id):
    payment = Payment.query.filter_by(transaction_id=transaction_id, user_id=current_user.id).first_or_404()
    return render_template('payment_checkout.html', payment=payment)

@app.route('/payment/bank-transfer/<transaction_id>', methods=['POST'])
@login_required
def bank_transfer_payment(transaction_id):
    payment = Payment.query.filter_by(transaction_id=transaction_id, user_id=current_user.id).first_or_404()
    reference = request.form.get('bank_reference', '').strip()
    bank = request.form.get('bank', '').strip()

    if not reference or bank not in ['NCB', 'JMMB', 'Scotiabank']:
        flash('Please choose a supported bank and enter your transfer reference.', 'danger')
        return redirect(url_for('payment_checkout', transaction_id=transaction_id))

    payment.status = 'pending'
    payment.discount_code = f"{payment.discount_code or ''} BANK:{bank} REF:{reference}"[:50]
    db.session.commit()
    flash('Bank transfer submitted. Your subscription will activate after payment confirmation.', 'info')
    return redirect(url_for('dashboard'))

@app.route('/payment/fygaro/webhook', methods=['POST'])
def fygaro_webhook():
    payload = request.get_json(silent=True) or request.form
    transaction_id = payload.get('transaction_id')
    status = payload.get('status')

    if status not in ['completed', 'paid', 'success']:
        return jsonify({'ok': False, 'message': 'Ignored non-success payment status'}), 202

    success, message = subscription_handler.confirm_payment(transaction_id)
    return jsonify({'ok': success, 'message': message}), 200 if success else 404

@app.route('/signals')
@login_required
def signals():
    signals = Trade.query.order_by(Trade.created_at.desc()).all()
    return render_template('signals.html', signals=signals)

@app.route('/classrooms')
@login_required
def classrooms():
    all_classrooms = Classroom.query.order_by(Classroom.updated_at.desc()).all()
    return render_template('classrooms.html', classrooms=all_classrooms)

@app.route('/classrooms/create', methods=['GET', 'POST'])
@login_required
def create_classroom():
    if current_user.role not in ['super_admin', 'admin', 'teacher']:
        flash('Only teachers and admins can create classrooms.', 'danger')
        return redirect(url_for('classrooms'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Classroom title is required.', 'danger')
            return redirect(url_for('create_classroom'))

        classroom = Classroom(title=title, description=description, teacher_id=current_user.id)
        db.session.add(classroom)
        db.session.commit()
        flash('Classroom created successfully.', 'success')
        return redirect(url_for('classrooms'))

    return render_template('classroom_form.html', classroom=None)

@app.route('/classrooms/<int:classroom_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_classroom(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    if current_user.role not in ['super_admin', 'admin'] and classroom.teacher_id != current_user.id:
        flash('You do not have permission to edit this classroom.', 'danger')
        return redirect(url_for('classrooms'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Classroom title is required.', 'danger')
            return redirect(url_for('edit_classroom', classroom_id=classroom.id))

        classroom.title = title
        classroom.description = description
        db.session.commit()
        flash('Classroom updated successfully.', 'success')
        return redirect(url_for('classrooms'))

    return render_template('classroom_form.html', classroom=classroom)

@app.route('/classrooms/<int:classroom_id>/materials/upload', methods=['POST'])
@login_required
def upload_material(classroom_id):
    classroom = Classroom.query.get_or_404(classroom_id)
    if current_user.role not in ['super_admin', 'admin'] and classroom.teacher_id != current_user.id:
        flash('Only the teacher or admins can upload materials.', 'danger')
        return redirect(url_for('classrooms'))

    file = request.files.get('material')
    title = request.form.get('title', '').strip()
    if not file or not file.filename:
        flash('Choose a file to upload.', 'danger')
        return redirect(url_for('classrooms'))

    original_filename = secure_filename(file.filename)
    stored_filename = f"{uuid4().hex}_{original_filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], stored_filename))

    material = ClassroomMaterial(
        classroom_id=classroom.id,
        title=title or original_filename,
        filename=stored_filename,
        original_filename=original_filename,
        uploaded_by=current_user.id
    )
    db.session.add(material)
    db.session.commit()
    flash('Material uploaded successfully.', 'success')
    return redirect(url_for('classrooms'))

@app.route('/classrooms/materials/<filename>')
@login_required
def download_material(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        audience = request.form.get('audience', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not all([name, email, audience, subject, message]):
            flash('Please complete all contact fields.', 'danger')
            return redirect(url_for('contact'))

        contact_message = ContactMessage(
            name=name,
            email=email,
            audience=audience,
            subject=subject,
            message=message
        )
        db.session.add(contact_message)
        db.session.commit()

        sent = notifier.send_contact_message(app.config.get('CONTACT_EMAIL'), name, email, audience, subject, message)
        flash('Message sent to Gmail successfully.' if sent else 'Message saved, but Gmail sending failed. Check SMTP settings.', 'success' if sent else 'warning')
        return redirect(url_for('contact'))

    return render_template('contact.html')

# Admin Routes
@app.route('/admin')
@login_required
@role_required(['super_admin', 'admin'])
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'active_subscriptions': Subscription.query.filter_by(is_active=True).count(),
        'total_trades': Trade.query.count(),
        'pending_trades': Trade.query.filter_by(status='pending').count(),
        'total_payments': Payment.query.filter_by(status='completed').count(),
        'revenue': db.session.query(db.func.sum(Payment.amount)).filter_by(status='completed').scalar() or 0
    }
    logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, logs=logs)

@app.route('/admin/users')
@login_required
@role_required(['super_admin', 'admin'])
def admin_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/roles')
@login_required
@role_required(['super_admin'])
def admin_roles():
    permissions = RolePermission.query.order_by(RolePermission.role, RolePermission.permission).all()
    return render_template('admin/manage_roles.html', permissions=permissions)

@app.route('/admin/roles/permissions/add', methods=['POST'])
@login_required
@role_required(['super_admin'])
def add_role_permission():
    role = request.form.get('role', '').strip()
    permission = request.form.get('permission', '').strip()

    if role not in ['super_admin', 'admin', 'teacher', 'student', 'user'] or not permission:
        flash('Choose a valid role and enter a permission.', 'danger')
        return redirect(url_for('admin_roles'))

    existing = RolePermission.query.filter_by(role=role, permission=permission).first()
    if existing:
        flash('That permission already exists for this role.', 'warning')
        return redirect(url_for('admin_roles'))

    db.session.add(RolePermission(role=role, permission=permission))
    db.session.commit()
    flash('Permission added successfully.', 'success')
    return redirect(url_for('admin_roles'))

@app.route('/admin/users/<int:user_id>/block', methods=['POST'])
@login_required
@role_required(['super_admin'])
def block_user(user_id):
    success, message = user_manager.block_user(user_id, current_user.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/unblock', methods=['POST'])
@login_required
@role_required(['super_admin'])
def unblock_user(user_id):
    success, message = user_manager.unblock_user(user_id, current_user.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/<int:user_id>/role', methods=['POST'])
@login_required
@role_required(['super_admin'])
def change_user_role(user_id):
    new_role = request.form.get('role')
    success, message = user_manager.change_role(user_id, new_role, current_user.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/trades')
@login_required
@role_required(['super_admin', 'admin'])
def admin_trades():
    trades = Trade.query.order_by(Trade.created_at.desc()).all()
    return render_template('admin/manage_trades.html', trades=trades)

@app.route('/admin/trades/create', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin'])
def create_trade():
    pair = request.form.get('pair')
    signal_type = request.form.get('signal_type')
    entry_condition = request.form.get('entry_condition')
    tp = request.form.get('tp')
    sl = request.form.get('sl')
    
    try:
        tp_value = float(tp) if tp else None
        sl_value = float(sl) if sl else None
    except ValueError:
        flash('Take profit and stop loss must be valid numbers.', 'danger')
        return redirect(url_for('admin_trades'))

    success, message = trade_manager.create_trade(
        pair, signal_type, entry_condition,
        tp_value,
        sl_value,
        current_user.id
    )
    
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin_trades'))

@app.route('/admin/trades/<int:trade_id>/delete', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin'])
def delete_trade(trade_id):
    success, message = trade_manager.delete_trade(trade_id, current_user.id)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('admin_trades'))

@app.route('/admin/pairs')
@login_required
@role_required(['super_admin', 'admin'])
def admin_pairs():
    pairs = TradingPair.query.all()
    return render_template('admin/manage_pairs.html', pairs=pairs)

@app.route('/admin/pairs/add', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin'])
def add_pair():
    pair_name = request.form.get('pair_name')
    
    existing = TradingPair.query.filter_by(pair_name=pair_name).first()
    if existing:
        flash('Pair already exists', 'danger')
    else:
        new_pair = TradingPair(pair_name=pair_name)
        db.session.add(new_pair)
        db.session.commit()
        activity_logger.log_activity(current_user.id, 'ADD_PAIR', f'Added trading pair {pair_name}', request.remote_addr)
        flash('Pair added successfully', 'success')
    
    return redirect(url_for('admin_pairs'))

@app.route('/admin/pairs/<int:pair_id>/toggle', methods=['POST'])
@login_required
@role_required(['super_admin', 'admin'])
def toggle_pair(pair_id):
    pair = TradingPair.query.get_or_404(pair_id)
    pair.is_active = not pair.is_active
    db.session.commit()
    status = 'activated' if pair.is_active else 'deactivated'
    activity_logger.log_activity(current_user.id, 'TOGGLE_PAIR', f'{status} pair {pair.pair_name}', request.remote_addr)
    flash(f'Pair {status}', 'success')
    return redirect(url_for('admin_pairs'))

@app.route('/admin/payments')
@login_required
@role_required(['super_admin', 'admin'])
def admin_payments():
    payments = Payment.query.order_by(Payment.created_at.desc()).all()
    return render_template('admin/payments.html', payments=payments)

@app.route('/admin/logs')
@login_required
@role_required(['super_admin'])
def admin_logs():
    logs = AdminLog.query.order_by(AdminLog.timestamp.desc()).limit(200).all()
    return render_template('admin/logs.html', logs=logs)

@app.route('/admin/security-events')
@login_required
@role_required(['super_admin'])
def security_events():
    events = SecurityEvent.query.order_by(SecurityEvent.timestamp.desc()).limit(200).all()
    return render_template('admin/security.html', events=events)

# API Routes
@app.route('/api/market-data/<pair>')
def market_data(pair):
    data = trading_engine.get_market_data(pair)
    if data is None:
        return jsonify({'error': 'Market data unavailable'}), 404

    return jsonify({
        'pair': pair,
        'candles': data.tail(50).to_dict(orient='records')
    })

@app.route('/api/check-signals')
@login_required
def check_signals():
    # Check pending signals
    pending_signals = Trade.query.filter_by(status='pending').all()
    results = []
    
    for signal in pending_signals:
        if trading_engine.check_condition(signal):
            # Execute signal
            success = signal_manager.execute_signal(signal.id)
            results.append({'signal_id': signal.id, 'executed': success})
    
    return jsonify(results)

@app.route('/api/user/signals')
@login_required
def user_signals():
    limit = request.args.get('limit', 20, type=int)
    signals = SignalHistory.query.filter_by(user_id=current_user.id)\
        .order_by(SignalHistory.sent_at.desc()).limit(limit).all()
    
    return jsonify([{
        'id': s.id,
        'pair': s.trade.pair,
        'type': s.trade.signal_type,
        'time': s.sent_at.isoformat()
    } for s in signals])

# Initialize database and create default admin
with app.app_context():
    db.create_all()
    init_default_admin(db, User)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
