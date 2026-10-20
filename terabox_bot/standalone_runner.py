"""
Zero-Dependency Standalone Telegram Long-Polling Engine
=====================================================
Uses Python 3 standard library (urllib.request, json, time, threading)
to poll Telegram Bot API updates, parse messages/callbacks, and execute handlers.
Runs anywhere Python 3 is installed without external pip packages.
"""

import json
import logging
import time
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

from .config import BotConfig
from .database import Database
from .terabox.account_manager import AccountManager
from .bot.handlers import BotHandlerService

logger = logging.getLogger(__name__)


class StandaloneTelegramBot:
    """Lightweight zero-dependency Telegram Bot API client and poller."""

    def __init__(self, token: str, handler_service: BotHandlerService):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.handler_service = handler_service
        self.offset = 0
        self.running = False

    def _call_api(self, method: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make an HTTP POST call to the Telegram Bot API."""
        url = f"{self.api_url}/{method}"
        data_bytes = json.dumps(payload or {}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            logger.error(f"Telegram API Error ({e.code}): {err_body}")
            try:
                return json.loads(err_body)
            except Exception:
                return {"ok": False, "description": f"HTTP {e.code}"}
        except Exception as e:
            logger.error(f"Network error calling Telegram {method}: {e}")
            return {"ok": False, "description": str(e)}

    def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[List[List[Dict[str, str]]]] = None
    ) -> Dict[str, Any]:
        """Send a message to a Telegram chat."""
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = {"inline_keyboard": reply_markup}

        return self._call_api("sendMessage", payload)

    def edit_message_text(
        self,
        chat_id: int,
        message_id: int,
        text: str,
        parse_mode: str = "HTML",
        reply_markup: Optional[List[List[Dict[str, str]]]] = None
    ) -> Dict[str, Any]:
        """Edit an existing message for snappy pagination and toggling."""
        payload: Dict[str, Any] = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        if reply_markup:
            payload["reply_markup"] = {"inline_keyboard": reply_markup}

        return self._call_api("editMessageText", payload)

    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None) -> None:
        """Acknowledge Telegram callback queries to dismiss the loading clock."""
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        self._call_api("answerCallbackQuery", payload)

    def process_update(self, update: Dict[str, Any]) -> None:
        """Route an incoming Telegram update to the proper handler."""
        # 1. Message Updates
        if "message" in update:
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg.get("from", {}).get("id", chat_id)
            first_name = msg.get("from", {}).get("first_name", "Friend")
            text = msg.get("text", "").strip()

            if not text:
                return

            if text.startswith("/start"):
                reply, kb = self.handler_service.handle_start(user_id, first_name)
            elif text.startswith("/help"):
                reply, kb = self.handler_service.handle_help(user_id)
            elif text.startswith("/status"):
                reply, kb = self.handler_service.handle_status(user_id)
            elif text.startswith("/accounts"):
                reply, kb = self.handler_service.handle_accounts(user_id)
            elif text.startswith("/addaccount"):
                args = text[len("/addaccount"):].strip()
                reply, kb = self.handler_service.handle_add_account(user_id, args)
            elif text.startswith("/toggleaccount"):
                args = text[len("/toggleaccount"):].strip()
                reply, kb = self.handler_service.handle_toggle_account(user_id, args)
            elif text.startswith("/delaccount"):
                args = text[len("/delaccount"):].strip()
                reply, kb = self.handler_service.handle_del_account(user_id, args)
            elif text.startswith("/sync"):
                args = text[len("/sync"):].strip()
                reply, kb = self.handler_service.handle_sync(user_id, args or None)
            elif text.startswith("/search"):
                query = text[len("/search"):].strip()
                reply, kb = self.handler_service.handle_search(query, page=1)
            else:
                # Any plain text message is treated as a search query!
                reply, kb = self.handler_service.handle_search(text, page=1)

            self.send_message(chat_id, reply, reply_markup=kb)

        # 2. Callback Queries (Inline buttons)
        elif "callback_query" in update:
            cb = update["callback_query"]
            cb_id = cb["id"]
            user_id = cb.get("from", {}).get("id", 0)
            data = cb.get("data", "")
            msg = cb.get("message")

            if not msg:
                self.answer_callback_query(cb_id)
                return

            chat_id = msg["chat"]["id"]
            message_id = msg["message_id"]

            reply_text, keyboard, should_edit = self.handler_service.handle_callback(user_id, data)
            self.answer_callback_query(cb_id)

            if should_edit:
                self.edit_message_text(chat_id, message_id, reply_text, reply_markup=keyboard)
            elif reply_text:
                self.send_message(chat_id, reply_text, reply_markup=keyboard)

    def start_polling(self) -> None:
        """Continuous polling loop."""
        print("\n=======================================================")
        print("  TeraBox Search Bot (Standalone Runner)")
        print("=======================================================")
        print(f"[*] Verifying Telegram bot token...")
        me = self._call_api("getMe")
        if not me.get("ok"):
            print(f"[!] ERROR: Failed to connect to Telegram: {me.get('description')}")
            print("    Please check TELEGRAM_BOT_TOKEN in your .env file.")
            return

        bot_username = me.get("result", {}).get("username", "UnknownBot")
        print(f"[+] Bot Authorized as @{bot_username}")
        print(f"[+] Admin ID: {BotConfig.ADMIN_TELEGRAM_ID or '(None configured)'}")
        print(f"[+] SQLite Database: {BotConfig.DB_PATH}")
        print(f"[*] Polling Telegram updates... (Press Ctrl+C to stop)\n")

        self.running = True
        while self.running:
            try:
                res = self._call_api("getUpdates", {"offset": self.offset, "timeout": 20})
                if res.get("ok"):
                    updates = res.get("result", [])
                    for u in updates:
                        self.offset = u["update_id"] + 1
                        self.process_update(u)
                else:
                    time.sleep(2)
            except KeyboardInterrupt:
                print("\n[!] Received shutdown signal. Exiting.")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Polling loop exception: {e}")
                time.sleep(3)
