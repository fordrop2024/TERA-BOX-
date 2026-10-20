"""
Telegram Message Formatters
===========================
Formats search results, system statistics, file metadata, and error messages
with emojis, clean typography, and HTML formatting for Telegram.
"""

import html
from typing import Any, Dict, List


def format_bytes(num_bytes: int) -> str:
    """Convert raw byte count into human-readable string (KB, MB, GB, TB)."""
    if not num_bytes or num_bytes <= 0:
        return "Unknown size"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0 or unit == "TB":
            return f"{num_bytes:.2f} {unit}" if unit != "B" else f"{int(num_bytes)} B"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"


def get_category_emoji(category: str) -> str:
    """Return appropriate emoji badge for file category."""
    cat_lower = (category or "").lower()
    mapping = {
        "video": "🎬",
        "audio": "🎵",
        "software": "💾",
        "archive": "📦",
        "document": "📚",
        "image": "🖼️",
        "folder": "📁"
    }
    return mapping.get(cat_lower, "📄")


def format_search_results(
    query: str,
    results: List[Dict[str, Any]],
    total: int,
    page: int,
    page_size: int
) -> str:
    """Format paginated search results into Telegram HTML message."""
    total_pages = max(1, (total + page_size - 1) // page_size)
    sanitized_query = html.escape(query)

    if not results:
        return (
            f"🔍 <b>Search Results for:</b> <code>{sanitized_query}</code>\n\n"
            "❌ <b>No matching files found.</b>\n\n"
            "💡 <b>Tips:</b>\n"
            "• Check spelling and try broader keywords (e.g. <code>Movie 1080p</code> instead of long hashes).\n"
            "• Ask an admin to verify connected accounts using <code>/accounts</code>.\n"
            "• Run <code>/sync</code> to index recent cloud additions."
        )

    lines = [
        f"🔍 <b>Search:</b> <code>{sanitized_query}</code>",
        f"📊 Found <b>{total}</b> match{'es' if total != 1 else ''} • <b>Page {page} of {total_pages}</b>\n"
    ]

    for idx, item in enumerate(results, 1):
        global_idx = (page - 1) * page_size + idx
        fname = html.escape(item.get("file_name", "Unknown File"))
        fsize = format_bytes(item.get("file_size", 0))
        cat = item.get("category", "Other")
        emoji = get_category_emoji(cat)
        acc_label = html.escape(item.get("account_label", "Unknown"))
        link_type = item.get("link_type", "share")
        type_badge = "⚡ Direct Ticket" if link_type == "direct" else "🔗 TeraBox Share"

        lines.append(
            f"<b>{global_idx}. {emoji} {fname}</b>\n"
            f"   📦 <code>{fsize}</code> | 🏷️ <code>{acc_label}</code> | {type_badge}\n"
        )

    lines.append(
        "<i>💡 Click the button below each item to open it in TeraBox (Web/App).</i>\n"
        "<i>⚠️ TeraBox requires login to stream/transfer; direct hotlinking is restricted.</i>"
    )

    return "\n".join(lines)


def format_file_details(item: Dict[str, Any]) -> str:
    """Format single file full metadata view."""
    fname = html.escape(item.get("file_name", "Unknown File"))
    fpath = html.escape(item.get("file_path", "/"))
    fsize = format_bytes(item.get("file_size", 0))
    cat = item.get("category", "Other")
    emoji = get_category_emoji(cat)
    acc = html.escape(item.get("account_label", "Unknown"))
    md5 = item.get("md5") or "N/A"
    link_type = item.get("link_type", "share")
    type_desc = "Direct Download Stream" if link_type == "direct" else "Official TeraBox Share Link"

    return (
        f"{emoji} <b>File Details</b>\n\n"
        f"📁 <b>Name:</b> <code>{fname}</code>\n"
        f"📂 <b>Path:</b> <code>{fpath}</code>\n"
        f"💾 <b>Size:</b> <code>{fsize}</code> ({item.get('file_size', 0):,} bytes)\n"
        f"🏷️ <b>Category:</b> {cat}\n"
        f"🏢 <b>Account:</b> <code>{acc}</code>\n"
        f"🔑 <b>MD5 Hash:</b> <code>{md5}</code>\n"
        f"🔗 <b>Link Type:</b> {type_desc}\n\n"
        f"<i>Tap below to open in your browser or TeraBox application.</i>"
    )


def format_status(stats: Dict[str, Any], is_admin: bool) -> str:
    """Format /status report with database and account metrics."""
    total_acc = stats.get("total_accounts", 0)
    active_acc = stats.get("active_accounts", 0)
    total_files = stats.get("total_files", 0)
    total_size = format_bytes(stats.get("total_bytes", 0))
    db_size = format_bytes(stats.get("db_size_bytes", 0))
    categories = stats.get("categories", {})

    cat_text = "\n".join([f"   • {get_category_emoji(k)} {k}: <b>{v:,}</b>" for k, v in categories.items()]) if categories else "   • (No files indexed yet)"

    admin_badge = "👑 <b>Admin View</b>" if is_admin else "👤 <b>User View</b>"

    return (
        f"🤖 <b>TeraBox Search Bot Status</b>\n"
        f"{admin_badge}\n\n"
        f"📊 <b>System Overview:</b>\n"
        f"   • <b>Connected Accounts:</b> {active_acc} active / {total_acc} total\n"
        f"   • <b>Indexed Files:</b> {total_files:,} files\n"
        f"   • <b>Total Volume:</b> {total_size}\n"
        f"   • <b>Database Storage:</b> {db_size}\n\n"
        f"📁 <b>Category Breakdown:</b>\n"
        f"{cat_text}\n\n"
        f"🟢 <b>Bot Backend:</b> Online & Responding"
    )


def format_accounts_list(accounts: List[Dict[str, Any]]) -> str:
    """Format /accounts list for admin management."""
    if not accounts:
        return (
            "⚙️ <b>TeraBox Account Connections</b>\n\n"
            "<i>No TeraBox accounts registered yet.</i>\n\n"
            "Use: <code>/addaccount &lt;label&gt; &lt;ndus_cookie&gt;</code> to connect one."
        )

    lines = [
        "⚙️ <b>Connected TeraBox Accounts</b>\n",
        f"Total Configured: <b>{len(accounts)}</b>\n"
    ]

    for acc in accounts:
        aid = acc["id"]
        label = html.escape(acc["label"])
        is_active = acc.get("is_active", 1)
        status_icon = "🟢 Active" if is_active else "🔴 Disabled"
        auth_status = acc.get("auth_status", "unverified")
        total_files = acc.get("total_files", 0)
        synced_at = acc.get("last_synced_at") or "Never"

        lines.append(
            f"<b>#{aid} — {label}</b>\n"
            f"   • Status: <b>{status_icon}</b> (Auth: <code>{auth_status}</code>)\n"
            f"   • Indexed Files: <b>{total_files:,}</b>\n"
            f"   • Last Sync: <code>{synced_at}</code>\n"
        )

    lines.append(
        "<i>Use /toggleaccount &lt;id&gt; to enable/disable.</i>\n"
        "<i>Use /delaccount &lt;id&gt; to remove an account.</i>\n"
        "<i>Use /sync to refresh indexed file catalog.</i>"
    )

    return "\n".join(lines)


def format_help_message(is_admin: bool) -> str:
    """Return user or admin help guide."""
    msg = (
        "📖 <b>TeraBox Search Bot — User Guide</b>\n\n"
        "<b>How to Search:</b>\n"
        "• Send any search query directly in chat, e.g.:\n"
        "  <code>Example Movie 1080p</code>\n"
        "  <code>Ubuntu 24.04</code>\n"
        "  <code>Python Masterclass</code>\n\n"
        "• Or use the command:\n"
        "  <code>/search &lt;keywords&gt;</code>\n\n"
        "<b>Features:</b>\n"
        "• Multi-term keyword filtering across all active accounts.\n"
        "• Inline clickable buttons to open official TeraBox links.\n"
        "• Interactive page navigation (Next / Prev).\n"
        "• Deduplication of matching files.\n\n"
        "<b>⚠️ Important TeraBox Limitation:</b>\n"
        "TeraBox share links open in your web browser or official TeraBox app. "
        "Direct CDN streaming without logging into TeraBox is restricted by TeraBox security measures.\n"
    )

    if is_admin:
        msg += (
            "\n👑 <b>Administrator Commands:</b>\n"
            "• <code>/status</code> — Bot metrics, memory, and database size.\n"
            "• <code>/accounts</code> — Manage connected TeraBox accounts.\n"
            "• <code>/addaccount &lt;label&gt; &lt;ndus&gt;</code> — Add new account.\n"
            "• <code>/toggleaccount &lt;id&gt;</code> — Enable/disable account.\n"
            "• <code>/delaccount &lt;id&gt;</code> — Remove account & clear files.\n"
            "• <code>/sync [label]</code> — Re-index remote files from cloud.\n"
        )

    return msg


def format_welcome_message(first_name: str, is_admin: bool) -> str:
    """Return welcome message on /start."""
    admin_note = "\n\n👑 <i>You are recognized as an Administrator. Type /help for admin controls.</i>" if is_admin else ""
    return (
        f"👋 <b>Welcome, {html.escape(first_name)}!</b>\n\n"
        "I am <b>TeraBox Search Bot</b> — your fast indexer for finding files across "
        "connected TeraBox cloud storage accounts.\n\n"
        "🔍 <b>Quick Start:</b>\n"
        "Simply type any keywords you are looking for, such as:\n"
        "👉 <code>Example Movie 1080p</code>\n"
        "👉 <code>Ubuntu</code>\n"
        "👉 <code>Python</code>\n\n"
        "I'll search all active accounts and return clickable download/share buttons right here in Telegram!"
        f"{admin_note}"
    )
