from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

class TelegramBot:
    def __init__(self, token, db, User, SignalManager):
        self.token = token
        self.db = db
        self.User = User
        self.signal_manager = SignalManager
        self.application = None
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Link Telegram chat with user account
        keyboard = [
            [InlineKeyboardButton("Link Account", callback_data='link_account')],
            [InlineKeyboardButton("Get Latest Signals", callback_data='get_signals')],
            [InlineKeyboardButton("Subscription Info", callback_data='sub_info')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"Welcome {user.first_name}! 🤖\n\n"
            f"I'm CryptoBot - Your automated trading assistant.\n\n"
            f"Please link your account to start receiving trading signals.",
            reply_markup=reply_markup
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == 'link_account':
            await query.edit_message_text(
                "To link your account, please use the /link command followed by your verification code.\n\n"
                "You can find your verification code in your CryptoBot dashboard under Account Settings."
            )
        
        elif query.data == 'get_signals':
            # Check if user is linked
            user = self.User.query.filter_by(telegram_chat_id=str(query.from_user.id)).first()
            if user:
                signals = self.signal_manager.get_pending_signals()
                if signals:
                    for signal in signals[:5]:
                        await query.message.reply_text(
                            f"📊 *Signal Alert*\n\n"
                            f"Pair: {signal.pair}\n"
                            f"Type: {signal.signal_type}\n"
                            f"Entry: {signal.entry_condition}\n"
                            f"TP: {signal.tp or 'N/A'}\n"
                            f"SL: {signal.sl or 'N/A'}",
                            parse_mode='Markdown'
                        )
                else:
                    await query.message.reply_text("No active signals at the moment.")
            else:
                await query.message.reply_text("Please link your account first using /link")
        
        elif query.data == 'sub_info':
            user = self.User.query.filter_by(telegram_chat_id=str(query.from_user.id)).first()
            if user:
                status = "✅ Active" if user.has_access() else "❌ Inactive"
                await query.message.reply_text(
                    f"*Subscription Information*\n\n"
                    f"Status: {status}\n"
                    f"Role: {user.role}\n"
                    f"Plan: {user.subscription_status}",
                    parse_mode='Markdown'
                )
            else:
                await query.message.reply_text("Please link your account first using /link")
    
    async def link_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /link command"""
        args = context.args
        if not args:
            await update.message.reply_text("Please provide your verification code. Usage: /link <code>")
            return
        
        code = args[0]
        # Verify code and link user
        user = self.User.query.filter_by(twofa_secret=code).first()
        if user:
            user.telegram_chat_id = str(update.effective_chat.id)
            self.db.session.commit()
            await update.message.reply_text("✅ Account linked successfully! You will now receive trading signals.")
        else:
            await update.message.reply_text("❌ Invalid verification code. Please check your dashboard.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
        *Available Commands*
        
        /start - Start the bot
        /help - Show this help message
        /link <code> - Link your account
        /signals - Get latest signals
        /status - Check subscription status
        /unlink - Unlink your account
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command"""
        user = self.User.query.filter_by(telegram_chat_id=str(update.effective_chat.id)).first()
        if user and user.has_access():
            signals = self.signal_manager.get_pending_signals()
            if signals:
                for signal in signals[:5]:
                    await update.message.reply_text(
                        f"📊 *{signal.signal_type} Signal*\n\n"
                        f"Pair: `{signal.pair}`\n"
                        f"Entry: {signal.entry_condition}\n"
                        f"TP: {signal.tp or 'N/A'}\n"
                        f"SL: {signal.sl or 'N/A'}",
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text("No active signals at the moment.")
        else:
            await update.message.reply_text("Please link your account and have an active subscription.")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user = self.User.query.filter_by(telegram_chat_id=str(update.effective_chat.id)).first()
        if user:
            status = "✅ Active" if user.has_access() else "❌ Inactive"
            await update.message.reply_text(
                f"*Account Status*\n\n"
                f"Status: {status}\n"
                f"Role: {user.role}\n"
                f"Email: {user.email}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("Account not linked. Use /link to connect.")
    
    async def unlink_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unlink command"""
        user = self.User.query.filter_by(telegram_chat_id=str(update.effective_chat.id)).first()
        if user:
            user.telegram_chat_id = None
            self.db.session.commit()
            await update.message.reply_text("Account unlinked successfully.")
        else:
            await update.message.reply_text("No account is currently linked.")
    
    def run(self):
        """Start the bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("link", self.link_command))
        self.application.add_handler(CommandHandler("signals", self.signals_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("unlink", self.unlink_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start the bot
        self.application.run_polling()