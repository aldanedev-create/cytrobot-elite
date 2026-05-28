from flask import jsonify, render_template, request
from flask_login import current_user

from database.models import SupportTicket
from support.chatbot import CustomerServiceBot
from support.faq_engine import get_suggestions


def register_support_routes(app, db, ActivityLogger):
    bot = CustomerServiceBot()

    @app.route('/support')
    def support_page():
        return render_template('support.html', suggestions=get_suggestions())

    @app.route('/api/support/chat', methods=['POST'])
    def support_chat():
        payload = request.get_json(silent=True) or {}
        question = payload.get('message', '')
        return jsonify(bot.reply(question))

    @app.route('/api/support/ticket', methods=['POST'])
    def support_ticket():
        payload = request.get_json(silent=True) or {}
        message = (payload.get('message') or '').strip()
        email = (payload.get('email') or '').strip()
        subject = (payload.get('subject') or 'Website support request').strip()

        if not message:
            return jsonify({'error': 'Please enter a message before opening a ticket.'}), 400

        ticket = SupportTicket(
            user_id=current_user.id if current_user.is_authenticated else None,
            email=current_user.email if current_user.is_authenticated else email or None,
            subject=subject[:150],
            message=message
        )
        db.session.add(ticket)
        db.session.commit()

        return jsonify({
            'ticket_id': ticket.id,
            'message': f'Support ticket #{ticket.id} opened. We will follow up soon.'
        })
