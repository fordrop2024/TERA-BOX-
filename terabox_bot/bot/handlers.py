"""
Telegram Bot Handlers
=====================
Command processors and callback query routers for TeraBox search and admin actions.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from ..config import BotConfig
from ..database import Database
from ..terabox.account_manager import AccountManager
from .formatters import (
    format_accounts_list,
    format_help_message,
    format_search_results,
    format_status,
    format_welcome_message,
)
from .keyboards import (
    build_account_admin_keyboard,
    build_search_keyboard,
)

logger = logging.getLogger(__name__)


class BotHandlerService:
    """Core logic for handling Telegram commands and search queries."""

    def __init__(self, db: Database, account_manager: AccountManager):
        self.db = db
        self.account_manager = account_manager
        self.page_size = BotConfig.DEFAULT_PAGE_SIZE

    def handle_start(self, user_id: int, first_name: str) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Respond to /start command."""
        is_admin = BotConfig.is_admin(user_id)
        text = format_welcome_message(first_name, is_admin)
        return text, None

    def handle_help(self, user_id: int) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Respond to /help command."""
        is_admin = BotConfig.is_admin(user_id)
        text = format_help_message(is_admin)
        return text, None

    def handle_search(self, query: str, page: int = 1) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Execute file search across active accounts with pagination."""
        cleaned_query = query.strip()
        if not cleaned_query:
            return "🔍 Please provide search keywords.\nExample: <code>/search Example Movie 1080p</code>", None

        offset = (page - 1) * self.page_size
        results, total = self.db.search_files(cleaned_query, limit=self.page_size, offset=offset)

        text = format_search_results(cleaned_query, results, total, page, self.page_size)
        keyboard = build_search_keyboard(results, cleaned_query, page, total, self.page_size) if total > 0 else None

        return text, keyboard

    def handle_status(self, user_id: int) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Respond to /status command."""
        is_admin = BotConfig.is_admin(user_id)
        if not is_admin:
            return "⛔ <b>Access Denied:</b> This command is restricted to the bot administrator.", None

        stats = self.db.get_stats()
        text = format_status(stats, is_admin=True)
        return text, None

    def handle_accounts(self, user_id: int) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Respond to /accounts command."""
        if not BotConfig.is_admin(user_id):
            return "⛔ <b>Access Denied:</b> Account management is restricted to the administrator.", None

        accounts = self.db.get_accounts()
        text = format_accounts_list(accounts)
        keyboard = build_account_admin_keyboard(accounts) if accounts else None
        return text, keyboard

    def handle_add_account(self, user_id: int, args_text: str) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Add new account connection: /addaccount <label> <ndus_cookie>."""
        if not BotConfig.is_admin(user_id):
            return "⛔ <b>Access Denied:</b> Admin credentials required.", None

        parts = args_text.strip().split(maxsplit=1)
        if len(parts) < 2:
            return (
                "⚠️ <b>Usage:</b> <code>/addaccount &lt;label&gt; &lt;ndus_cookie&gt;</code>\n\n"
                "Example: <code>/addaccount MyCloud ndus_cookie_value_from_browser</code>",
                None
            )

        label, ndus = parts[0].strip(), parts[1].strip()

        # Save to database
        acc_id = self.db.add_account(label=label, ndus_cookie=ndus)

        # Test connection immediately
        verify_result = self.account_manager.verify_account(acc_id)
        if verify_result["success"]:
            details = verify_result["details"]
            uname = details.get("username", "Connected User")
            return (
                f"✅ <b>Account Added & Verified Successfully!</b>\n\n"
                f"• <b>Label:</b> <code>{label}</code> (ID: #{acc_id})\n"
                f"• <b>TeraBox User:</b> <code>{uname}</code>\n"
                f"• <b>Status:</b> Ready for indexing\n\n"
                f"👉 Run <code>/sync</code> to index its files into the search catalog.",
                None
            )
        else:
            err = verify_result["details"].get("error", "Unknown verification error")
            return (
                f"⚠️ <b>Account Saved but Verification Failed</b>\n\n"
                f"• <b>Label:</b> <code>{label}</code> (ID: #{acc_id})\n"
                f"• <b>Error:</b> <code>{err}</code>\n\n"
                f"Please ensure the NDUS cookie was copied correctly without trailing spaces.",
                None
            )

    def handle_toggle_account(self, user_id: int, account_id_or_label: str) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Enable or disable an account: /toggleaccount <id>."""
        if not BotConfig.is_admin(user_id):
            return "⛔ <b>Access Denied:</b> Admin only.", None

        try:
            aid = int(account_id_or_label.strip())
            acc = self.db.get_account(aid)
        except ValueError:
            acc = self.db.get_account_by_label(account_id_or_label.strip())

        if not acc:
            return f"❌ Account '{account_id_or_label}' not found.", None

        new_status = not bool(acc["is_active"])
        self.db.toggle_account(acc["id"], is_active=new_status)
        state_str = "🟢 Enabled" if new_status else "🔴 Disabled"
        return f"⚙️ Account <b>{acc['label']}</b> (ID: #{acc['id']}) is now <b>{state_str}</b>.", None

    def handle_del_account(self, user_id: int, account_id_or_label: str) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Delete an account: /delaccount <id>."""
        if not BotConfig.is_admin(user_id):
            return "⛔ <b>Access Denied:</b> Admin only.", None

        try:
            aid = int(account_id_or_label.strip())
            acc = self.db.get_account(aid)
        except ValueError:
            acc = self.db.get_account_by_label(account_id_or_label.strip())

        if not acc:
            return f"❌ Account '{account_id_or_label}' not found.", None

        self.db.delete_account(acc["id"])
        return f"🗑️ Account <b>{acc['label']}</b> (ID: #{acc['id']}) and all its indexed files have been removed.", None

    def handle_sync(self, user_id: int, label_arg: Optional[str] = None) -> Tuple[str, Optional[List[List[Dict[str, str]]]]]:
        """Re-index remote files from cloud accounts: /sync [label]."""
        if not BotConfig.is_admin(user_id):
            return "⛔ <b>Access Denied:</b> Sync is restricted to administrators.", None

        if label_arg and label_arg.strip():
            acc = self.db.get_account_by_label(label_arg.strip())
            if not acc:
                return f"❌ Account with label '{label_arg}' not found.", None
            results = [self.account_manager.sync_account(acc["id"])]
        else:
            results = self.account_manager.sync_all_accounts()

        if not results:
            return "ℹ️ No active accounts found to sync. Use <code>/accounts</code> to configure one.", None

        lines = ["🔄 <b>TeraBox Cloud Sync Report:</b>\n"]
        for res in results:
            lbl = res.get("label", "Unknown")
            if res.get("success"):
                cnt = res.get("total_indexed", 0)
                lines.append(f"✅ <b>{lbl}:</b> {cnt:,} files indexed")
            else:
                err = res.get("error", "Failed")
                lines.append(f"❌ <b>{lbl}:</b> Error — <code>{err}</code>")

        return "\n".join(lines), None

    def handle_callback(self, user_id: int, data: str) -> Tuple[str, Optional[List[List[Dict[str, str]]]], bool]:
        """
        Handle inline button callback queries (pagination, toggle, sync).
        Returns (response_text, optional_keyboard, edit_message_flag).
        """
        if data.startswith("noop"):
            return "You are currently on this page.", None, False

        # Pagination: page:<query>:<page_num>
        if data.startswith("page:"):
            parts = data.split(":", 2)
            if len(parts) == 3:
                query = parts[1]
                page_num = int(parts[2])
                text, keyboard = self.handle_search(query, page=page_num)
                return text, keyboard, True

        # Admin toggle account: acc_toggle:<aid>
        if data.startswith("acc_toggle:"):
            if not BotConfig.is_admin(user_id):
                return "⛔ Admin permission required.", None, False
            aid = int(data.split(":")[1])
            self.db.toggle_account(aid)
            # Return refreshed accounts list
            accounts = self.db.get_accounts()
            return format_accounts_list(accounts), build_account_admin_keyboard(accounts), True

        # Admin sync account: acc_sync:<aid>
        if data.startswith("acc_sync:"):
            if not BotConfig.is_admin(user_id):
                return "⛔ Admin permission required.", None, False
            aid = int(data.split(":")[1])
            res = self.account_manager.sync_account(aid)
            msg = f"✅ Synced {res.get('total_indexed', 0)} files" if res.get("success") else f"❌ Sync failed: {res.get('error')}"
            accounts = self.db.get_accounts()
            return f"{format_accounts_list(accounts)}\n\n<i>{msg}</i>", build_account_admin_keyboard(accounts), True

        return "Unknown button action.", None, False
