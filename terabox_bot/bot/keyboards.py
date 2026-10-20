"""
Telegram Inline Keyboards
=========================
Generates inline keyboard markups for file links, pagination, and admin actions.
Compatible with python-telegram-bot or standard Telegram Bot API JSON structures.
"""

from typing import Any, Dict, List, Optional


def build_search_keyboard(
    results: List[Dict[str, Any]],
    query: str,
    page: int,
    total: int,
    page_size: int
) -> List[List[Dict[str, str]]]:
    """
    Build inline keyboard matrix containing:
    1. Direct URL buttons to open each matching file on TeraBox.
    2. Interactive pagination buttons (Prev, Page indicator, Next).
    """
    keyboard: List[List[Dict[str, str]]] = []
    total_pages = max(1, (total + page_size - 1) // page_size)

    # 1. URL Buttons for each file on this page
    for idx, item in enumerate(results, 1):
        global_idx = (page - 1) * page_size + idx
        fname = item.get("file_name", "File")
        # Truncate filename for button label
        short_name = (fname[:25] + "...") if len(fname) > 28 else fname
        share_url = item.get("share_url") or "https://terabox.com"

        keyboard.append([
            {
                "text": f"🔗 #{global_idx} Open {short_name}",
                "url": share_url
            }
        ])

    # 2. Pagination Navigation Row
    nav_row: List[Dict[str, str]] = []

    # Safe callback query truncation: Telegram callback_data limit is 64 bytes
    safe_query = query[:20].strip()

    if page > 1:
        nav_row.append({
            "text": "◀ Prev",
            "callback_data": f"page:{safe_query}:{page - 1}"
        })

    nav_row.append({
        "text": f"📄 {page}/{total_pages}",
        "callback_data": f"noop:{page}"
    })

    if page < total_pages:
        nav_row.append({
            "text": "Next ▶",
            "callback_data": f"page:{safe_query}:{page + 1}"
        })

    if nav_row:
        keyboard.append(nav_row)

    return keyboard


def build_account_admin_keyboard(accounts: List[Dict[str, Any]]) -> List[List[Dict[str, str]]]:
    """Build inline buttons for managing accounts (toggle / sync)."""
    keyboard: List[List[Dict[str, str]]] = []

    for acc in accounts:
        aid = acc["id"]
        label = acc["label"]
        is_active = acc.get("is_active", 1)
        toggle_icon = "⏸️ Disable" if is_active else "▶️ Enable"

        keyboard.append([
            {
                "text": f"{toggle_icon} #{aid} {label[:12]}",
                "callback_data": f"acc_toggle:{aid}"
            },
            {
                "text": f"🔄 Sync #{aid}",
                "callback_data": f"acc_sync:{aid}"
            }
        ])

    return keyboard
