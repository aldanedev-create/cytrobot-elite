FAQS = [
    {
        'category': 'payment',
        'keywords': ['subscribe', 'subscription', 'plan', 'payment', 'card', 'visa', 'mastercard', 'fygaro'],
        'answer': 'To subscribe, choose the Basic Plan from your dashboard. Card payments are handled through a secure payment gateway such as Fygaro, which supports Visa and Mastercard.'
    },
    {
        'category': 'bank_transfer',
        'keywords': ['bank', 'transfer', 'ncb', 'jmmb', 'scotiabank', 'scotia'],
        'answer': 'Bank transfers are supported for NCB, JMMB, and Scotiabank. Start a bank-transfer checkout from the dashboard, then submit the transfer reference so support can confirm it.'
    },
    {
        'category': 'telegram',
        'keywords': ['telegram', 'chat id', 'botfather', 'connect telegram'],
        'answer': 'Add your Telegram Chat ID in Account Settings. If you need help finding it, open the chat widget and create a support ticket with your Telegram username.'
    },
    {
        'category': 'trading',
        'keywords': ['buy', 'sell', 'signal', 'trading', 'take profit', 'stop loss', 'tp', 'sl'],
        'answer': 'A BUY signal means the system found conditions that may support a long entry. TP means take profit, and SL means stop loss. Always use proper position sizing.'
    },
    {
        'category': 'password',
        'keywords': ['password', 'reset', 'forgot', 'login', 'sign in'],
        'answer': 'Use Forgot Password on the login page. If your email is registered, the site sends a reset link through the configured Gmail SMTP account.'
    },
    {
        'category': '2fa',
        'keywords': ['2fa', 'two factor', 'verification code', 'gmail', 'authenticator', 'qr'],
        'answer': 'This site uses email-based 2FA. No QR code or Google Authenticator app is required. A 6-digit code is sent to your account email when verification is needed.'
    }
]


def find_faq_answer(question):
    normalized = (question or '').lower()
    for item in FAQS:
        if any(keyword in normalized for keyword in item['keywords']):
            return item['answer'], item['category']

    return None, None


def get_suggestions():
    return [
        'How do I subscribe?',
        'How do I connect Telegram?',
        'What does BUY signal mean?',
        'How do I reset my password?',
        'How do bank transfers work?'
    ]
