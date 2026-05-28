// Authentication JavaScript

// Login form handler
function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const remember = document.getElementById('remember')?.checked || false;
        
        if (!email || !password) {
            showNotification('Please fill in all fields', 'danger');
            return;
        }
        
        showLoading('loginBtn', 'Logging in...');
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    email: email,
                    password: password,
                    remember: remember
                })
            });
            
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                if (data.requires_2fa) {
                    window.location.href = '/verify-2fa';
                } else if (data.error) {
                    showNotification(data.error, 'danger');
                }
            }
        } catch (error) {
            console.error('Login error:', error);
            showNotification('Login failed. Please try again.', 'danger');
        } finally {
            hideLoading('loginBtn', 'Login');
        }
    });
}

// Registration form handler
function initRegisterForm() {
    const form = document.getElementById('registerForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm_password').value;
        
        // Validation
        if (username.length < 3 || username.length > 50) {
            showNotification('Username must be between 3 and 50 characters', 'danger');
            return;
        }
        
        if (!email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
            showNotification('Invalid email format', 'danger');
            return;
        }
        
        if (password.length < 8) {
            showNotification('Password must be at least 8 characters', 'danger');
            return;
        }
        
        if (password !== confirm) {
            showNotification('Passwords do not match', 'danger');
            return;
        }
        
        showLoading('registerBtn', 'Creating account...');
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    email: email,
                    password: password,
                    confirm_password: confirm
                })
            });
            
            if (response.redirected) {
                showNotification('Registration successful! Please login.', 'success');
                setTimeout(() => {
                    window.location.href = response.url;
                }, 2000);
            } else {
                const data = await response.json();
                showNotification(data.error || 'Registration failed', 'danger');
            }
        } catch (error) {
            console.error('Registration error:', error);
            showNotification('Registration failed. Please try again.', 'danger');
        } finally {
            hideLoading('registerBtn', 'Register');
        }
    });
}

// 2FA verification handler
function init2FAForm() {
    const form = document.getElementById('twofaForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const code = document.getElementById('code').value;
        
        if (!code || code.length !== 6 || !/^\d+$/.test(code)) {
            showNotification('Please enter a valid 6-digit code', 'danger');
            return;
        }
        
        showLoading('verifyBtn', 'Verifying...');
        
        try {
            const response = await fetch('/verify-2fa', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ code: code })
            });
            
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
                showNotification(data.error || 'Invalid code', 'danger');
            }
        } catch (error) {
            console.error('2FA error:', error);
            showNotification('Verification failed', 'danger');
        } finally {
            hideLoading('verifyBtn', 'Verify');
        }
    });
}

// Forgot password handler
function initForgotPasswordForm() {
    const form = document.getElementById('forgotPasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        
        if (!email) {
            showNotification('Please enter your email', 'danger');
            return;
        }
        
        showLoading('sendBtn', 'Sending...');
        
        try {
            const response = await fetch('/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ email: email })
            });
            
            showNotification('If an account exists with this email, you will receive a reset link.', 'success');
            form.reset();
        } catch (error) {
            console.error('Password reset error:', error);
            showNotification('Failed to send reset link', 'danger');
        } finally {
            hideLoading('sendBtn', 'Send Reset Link');
        }
    });
}

// Reset password handler
function initResetPasswordForm() {
    const form = document.getElementById('resetPasswordForm');
    if (!form) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm_password').value;
        
        if (password.length < 8) {
            showNotification('Password must be at least 8 characters', 'danger');
            return;
        }
        
        if (password !== confirm) {
            showNotification('Passwords do not match', 'danger');
            return;
        }
        
        showLoading('resetBtn', 'Resetting...');
        form.submit();
    });
}

// Session timeout handler
let sessionTimeout;
const SESSION_TIMEOUT = 30 * 60 * 1000; // 30 minutes

function resetSessionTimeout() {
    if (sessionTimeout) {
        clearTimeout(sessionTimeout);
    }
    
    sessionTimeout = setTimeout(() => {
        if (window.location.pathname !== '/login') {
            showNotification('Session expired. Please login again.', 'warning');
            setTimeout(() => {
                window.location.href = '/logout';
            }, 3000);
        }
    }, SESSION_TIMEOUT);
}

// Track user activity
function initSessionTracking() {
    const events = ['mousemove', 'keypress', 'click', 'scroll'];
    events.forEach(event => {
        document.addEventListener(event, resetSessionTimeout);
    });
    resetSessionTimeout();
}

// Logout handler
function initLogoutButton() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            try {
                const response = await fetch('/logout');
                if (response.redirected) {
                    window.location.href = response.url;
                }
            } catch (error) {
                console.error('Logout error:', error);
                window.location.href = '/logout';
            }
        });
    }
}

// Password strength checker
function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    if (!passwordInput) return;
    
    passwordInput.addEventListener('input', (e) => {
        const password = e.target.value;
        const strength = calculatePasswordStrength(password);
        updateStrengthIndicator(strength);
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    if (score <= 2) return 'weak';
    if (score <= 4) return 'medium';
    return 'strong';
}

function updateStrengthIndicator(strength) {
    let indicator = document.getElementById('password-strength');
    if (!indicator) {
        const passwordGroup = document.querySelector('#password').closest('.form-group');
        if (passwordGroup) {
            indicator = document.createElement('div');
            indicator.id = 'password-strength';
            indicator.className = 'password-strength mt-1';
            passwordGroup.appendChild(indicator);
        }
    }
    
    if (indicator) {
        indicator.className = `password-strength strength-${strength} mt-1`;
        const texts = { weak: 'Weak', medium: 'Medium', strong: 'Strong' };
        indicator.innerHTML = `<small>Password strength: ${texts[strength]}</small>`;
    }
}

// Initialize all auth functions
document.addEventListener('DOMContentLoaded', () => {
    initLoginForm();
    initRegisterForm();
    init2FAForm();
    initForgotPasswordForm();
    initResetPasswordForm();
    initLogoutButton();
    initPasswordStrength();
    
    // Only track session for authenticated pages
    if (document.querySelector('.dashboard-container')) {
        initSessionTracking();
    }
});