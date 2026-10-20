#!/usr/bin/env python3
"""
TeraBox Search Bot — Primary Entry Point
========================================
Main launcher for the Telegram bot. Automatically initializes SQLite storage,
seeds initial sample data if configured, and starts polling Telegram updates.

Supports both python-telegram-bot (v20+) and zero-dependency standalone mode.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from terabox_bot.config import BotConfig
from terabox_bot.database import Database
from terabox_bot.seed_data import seed_database
from terabox_bot.terabox.account_manager import AccountManager
from terabox_bot.bot.handlers import BotHandlerService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("terabox_bot")


def init_application() -> tuple[Database, AccountManager, BotHandlerService]:
    """Initialize database, seed sample data, and configure handler service."""
    # 1. Initialize SQLite Database
    db = Database(BotConfig.DB_PATH)
    logger.info(f"SQLite database initialized at: {BotConfig.DB_PATH}")

    # 2. Seed Sample Data if configured
    if BotConfig.ENABLE_SAMPLE_DATA:
        seed_database(db, force=False)
        stats = db.get_stats()
        logger.info(
            f"Sample data ready: {stats['total_files']} files across {stats['total_accounts']} accounts."
        )

    # 3. Check for default TeraBox account from .env
    if BotConfig.DEFAULT_ACCOUNT_NDUS and BotConfig.DEFAULT_ACCOUNT_NDUS != "":
        existing = db.get_account_by_label(BotConfig.DEFAULT_ACCOUNT_LABEL)
        if not existing:
            acc_id = db.add_account(
                label=BotConfig.DEFAULT_ACCOUNT_LABEL,
                ndus_cookie=BotConfig.DEFAULT_ACCOUNT_NDUS
            )
            logger.info(f"Registered default TeraBox account '{BotConfig.DEFAULT_ACCOUNT_LABEL}' (ID: #{acc_id})")

    # 4. Initialize Managers
    acc_manager = AccountManager(db)
    handler_service = BotHandlerService(db, acc_manager)

    return db, acc_manager, handler_service


def run_with_python_telegram_bot(handler_service: BotHandlerService) -> None:
    """Run bot using modern python-telegram-bot (v20+ async Application)."""
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        CallbackQueryHandler,
        ContextTypes,
        filters
    )

    def convert_keyboard(matrix):
        if not matrix:
            return None
        rows = []
        for row in matrix:
            btns = []
            for b in row:
                if "url" in b:
                    btns.append(InlineKeyboardButton(text=b["text"], url=b["url"]))
                else:
                    btns.append(InlineKeyboardButton(text=b["text"], callback_data=b["callback_data"]))
            rows.append(btns)
        return InlineKeyboardMarkup(rows)

    async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        text, _ = handler_service.handle_start(user.id, user.first_name)
        await update.message.reply_html(text)

    async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text, _ = handler_service.handle_help(update.effective_user.id)
        await update.message.reply_html(text)

    async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text, _ = handler_service.handle_status(update.effective_user.id)
        await update.message.reply_html(text)

    async def accounts_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text, kb = handler_service.handle_accounts(update.effective_user.id)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb))

    async def add_account_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        args_text = " ".join(context.args) if context.args else ""
        text, kb = handler_service.handle_add_account(update.effective_user.id, args_text)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb))

    async def toggle_account_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        arg = context.args[0] if context.args else ""
        text, kb = handler_service.handle_toggle_account(update.effective_user.id, arg)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb))

    async def del_account_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        arg = context.args[0] if context.args else ""
        text, kb = handler_service.handle_del_account(update.effective_user.id, arg)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb))

    async def sync_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        arg = context.args[0] if context.args else None
        text, kb = handler_service.handle_sync(update.effective_user.id, arg)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb))

    async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = " ".join(context.args) if context.args else ""
        text, kb = handler_service.handle_search(query, page=1)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb), disable_web_page_preview=True)

    async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Plain text is treated as a search query
        query = update.message.text
        text, kb = handler_service.handle_search(query, page=1)
        await update.message.reply_html(text, reply_markup=convert_keyboard(kb), disable_web_page_preview=True)

    async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        text, kb, should_edit = handler_service.handle_callback(query.from_user.id, query.data)
        if should_edit:
            await query.edit_message_text(text, parse_mode="HTML", reply_markup=convert_keyboard(kb), disable_web_page_preview=True)
        elif text:
            await query.message.reply_html(text, reply_markup=convert_keyboard(kb), disable_web_page_preview=True)

    app = ApplicationBuilder().token(BotConfig.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("accounts", accounts_cmd))
    app.add_handler(CommandHandler("addaccount", add_account_cmd))
    app.add_handler(CommandHandler("toggleaccount", toggle_account_cmd))
    app.add_handler(CommandHandler("delaccount", del_account_cmd))
    app.add_handler(CommandHandler("sync", sync_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))
    app.add_handler(CallbackQueryHandler(callback_handler))

    logger.info("Starting python-telegram-bot polling engine...")
    app.run_polling()


def main():
    """Main execution orchestrator."""
    print("=" * 60)
    print("  TeraBox Search Bot — Telegram Cloud File Indexer")
    print("=" * 60)

    # Validate settings
    issues = BotConfig.validate()
    if issues:
        print("\n[!] Configuration Warnings:")
        for issue in issues:
            print(f"    - {issue}")
        print("\n[i] Note: To configure your Telegram Bot Token and Admin ID:")
        print("    1. Copy .env.example to .env")
        print("    2. Set TELEGRAM_BOT_TOKEN and ADMIN_TELEGRAM_ID")
        print("    3. Run python main.py again\n")

    db, acc_manager, handler_service = init_application()

    if not BotConfig.TELEGRAM_BOT_TOKEN or BotConfig.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("[!] Stopping: A valid TELEGRAM_BOT_TOKEN is required to connect to Telegram.")
        print("    You can still test search logic by running: python run_tests.py\n")
        sys.exit(0)

    # Check which runner to use
    try:
        import telegram
        logger.info(f"Using python-telegram-bot v{telegram.__version__}")
        run_with_python_telegram_bot(handler_service)
    except ImportError:
        logger.info("python-telegram-bot not found in environment. Falling back to zero-dependency standalone runner.")
        from terabox_bot.standalone_runner import StandaloneTelegramBot
        bot = StandaloneTelegramBot(BotConfig.TELEGRAM_BOT_TOKEN, handler_service)
        bot.start_polling()


if __name__ == "__main__":
    main()
