"""
Configuration Loader
====================
Loads settings from environment variables and .env file with safe fallbacks.
"""

import os
from pathlib import Path


def load_env_file(filepath: Path = Path(".env")) -> None:
    """Safely parse .env file into os.environ if dotenv library is not installed."""
    if not filepath.exists():
        return
    try:
        # Try using python-dotenv if present
        from dotenv import load_dotenv
        load_dotenv(filepath)
    except ImportError:
        # Fallback to manual line parser
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val


# Load .env at module import
load_env_file()


class BotConfig:
    """Central bot configuration container."""

    # Telegram Credentials
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

    # Administrator ID
    _admin_id_raw: str = os.getenv("ADMIN_TELEGRAM_ID", "0").strip()
    try:
        ADMIN_TELEGRAM_ID: int = int(_admin_id_raw)
    except ValueError:
        ADMIN_TELEGRAM_ID: int = 0

    # Database
    DB_PATH: str = os.getenv("DB_PATH", "data/terabox_search.db").strip()
    ENABLE_SAMPLE_DATA: bool = os.getenv("ENABLE_SAMPLE_DATA", "true").lower() in ("1", "true", "yes")

    # Search Options
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "5"))
    TERABOX_REQUEST_TIMEOUT: int = int(os.getenv("TERABOX_REQUEST_TIMEOUT", "15"))

    # Initial TeraBox account credentials from .env (optional)
    DEFAULT_ACCOUNT_LABEL: str = os.getenv("TERABOX_ACCOUNT_1_LABEL", "Primary-Cloud").strip()
    DEFAULT_ACCOUNT_NDUS: str = os.getenv("TERABOX_ACCOUNT_1_NDUS", "").strip()

    @classmethod
    def is_admin(cls, user_id: int) -> bool:
        """Check if a given Telegram User ID matches the configured administrator."""
        if not cls.ADMIN_TELEGRAM_ID:
            return False
        return user_id == cls.ADMIN_TELEGRAM_ID

    @classmethod
    def validate(cls) -> list[str]:
        """Validate critical configuration and return list of warnings/errors."""
        issues = []
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            issues.append("TELEGRAM_BOT_TOKEN is missing or not set in .env")
        if cls.ADMIN_TELEGRAM_ID == 0:
            issues.append("ADMIN_TELEGRAM_ID is unset. Admin commands will be locked.")
        return issues
