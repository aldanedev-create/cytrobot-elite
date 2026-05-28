FALLBACK_RESPONSE = (
    "I can help with account access, subscriptions, payments, Telegram setup, "
    "trading signals, and password resets. Try one of the FAQ buttons, or create "
    "a support ticket and the team can follow up."
)


def build_response(question):
    normalized = (question or '').strip()
    if not normalized:
        return 'Ask me about your account, subscription, payments, Telegram setup, trading signals, or password reset.'

    return FALLBACK_RESPONSE
