"""
SQLite Database Layer
=====================
High-performance SQLite storage with token-based indexing, account isolation,
and full-text search capability for TeraBox files.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class Database:
    """Manages SQLite storage for accounts and indexed TeraBox files."""

    def __init__(self, db_path: str = "data/terabox_search.db"):
        self.db_path = db_path
        # Ensure directory exists
        db_file = Path(self.db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)
        self.has_fts = False
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection."""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self) -> None:
        """Create tables, indexes, and optional full-text search tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Accounts Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT UNIQUE NOT NULL,
                    ndus_cookie TEXT,
                    app_id TEXT DEFAULT '250528',
                    is_active INTEGER DEFAULT 1,
                    auth_status TEXT DEFAULT 'unverified',
                    total_files INTEGER DEFAULT 0,
                    last_synced_at TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # 2. Files Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    fs_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT DEFAULT '/',
                    file_size INTEGER DEFAULT 0,
                    is_dir INTEGER DEFAULT 0,
                    category TEXT DEFAULT 'Other',
                    share_url TEXT NOT NULL,
                    direct_url TEXT,
                    link_type TEXT DEFAULT 'share',
                    md5 TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
                    UNIQUE(account_id, fs_id)
                )
            """)

            # Indexes for quick lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_name ON files(file_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_account ON files(account_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")

            # Check if FTS5 is available in this SQLite build
            try:
                cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(file_name, file_path, category, content=files, content_rowid=id)")
                self.has_fts = True
            except sqlite3.OperationalError:
                # FTS5 module not compiled in; regular indexed LIKE search will be used
                self.has_fts = False

            conn.commit()

    # -------------------------------------------------------------------------
    # Account Management
    # -------------------------------------------------------------------------

    def add_account(self, label: str, ndus_cookie: str = "", app_id: str = "250528", is_active: int = 1) -> int:
        """Add a new TeraBox account or update its cookie if label exists."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO accounts (label, ndus_cookie, app_id, is_active, auth_status, created_at)
                VALUES (?, ?, ?, ?, 'unverified', ?)
                ON CONFLICT(label) DO UPDATE SET
                    ndus_cookie = excluded.ndus_cookie,
                    app_id = excluded.app_id,
                    is_active = excluded.is_active,
                    auth_status = 'unverified'
            """, (label, ndus_cookie, app_id, is_active, now))
            conn.commit()
            return cursor.lastrowid or 0

    def get_accounts(self, active_only: bool = False) -> List[Dict[str, Any]]:
        """Retrieve all registered TeraBox accounts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM accounts"
            if active_only:
                query += " WHERE is_active = 1"
            query += " ORDER BY id ASC"
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve account by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_account_by_label(self, label: str) -> Optional[Dict[str, Any]]:
        """Retrieve account by label."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE label = ?", (label,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def toggle_account(self, account_id: int, is_active: Optional[bool] = None) -> bool:
        """Toggle account active state."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if is_active is None:
                cursor.execute("UPDATE accounts SET is_active = 1 - is_active WHERE id = ?", (account_id,))
            else:
                cursor.execute("UPDATE accounts SET is_active = ? WHERE id = ?", (1 if is_active else 0, account_id))
            conn.commit()
            return cursor.rowcount > 0

    def update_account_status(self, account_id: int, auth_status: str, total_files: Optional[int] = None) -> None:
        """Update account verification status and last sync time."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if total_files is not None:
                cursor.execute("""
                    UPDATE accounts
                    SET auth_status = ?, total_files = ?, last_synced_at = ?
                    WHERE id = ?
                """, (auth_status, total_files, now, account_id))
            else:
                cursor.execute("""
                    UPDATE accounts
                    SET auth_status = ?, last_synced_at = ?
                    WHERE id = ?
                """, (auth_status, now, account_id))
            conn.commit()

    def delete_account(self, account_id: int) -> bool:
        """Remove account and all its indexed files."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            conn.commit()
            return cursor.rowcount > 0

    # -------------------------------------------------------------------------
    # File Indexing & Search
    # -------------------------------------------------------------------------

    def upsert_file(
        self,
        account_id: int,
        fs_id: str,
        file_name: str,
        file_path: str,
        file_size: int,
        is_dir: int,
        category: str,
        share_url: str,
        direct_url: Optional[str] = None,
        link_type: str = "share",
        md5: Optional[str] = None
    ) -> int:
        """Insert or update indexed file entry."""
        now = datetime.utcnow().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (
                    account_id, fs_id, file_name, file_path, file_size,
                    is_dir, category, share_url, direct_url, link_type, md5,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(account_id, fs_id) DO UPDATE SET
                    file_name = excluded.file_name,
                    file_path = excluded.file_path,
                    file_size = excluded.file_size,
                    is_dir = excluded.is_dir,
                    category = excluded.category,
                    share_url = excluded.share_url,
                    direct_url = excluded.direct_url,
                    link_type = excluded.link_type,
                    md5 = excluded.md5,
                    updated_at = excluded.updated_at
            """, (
                account_id, str(fs_id), file_name, file_path, file_size,
                is_dir, category, share_url, direct_url, link_type, md5,
                now, now
            ))
            file_id = cursor.lastrowid
            conn.commit()
            return file_id or 0

    def clear_account_files(self, account_id: int) -> int:
        """Remove all indexed files for a given account before re-indexing."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE account_id = ?", (account_id,))
            deleted = cursor.rowcount
            cursor.execute("UPDATE accounts SET total_files = 0 WHERE id = ?", (account_id,))
            conn.commit()
            return deleted

    def search_files(
        self,
        query: str,
        limit: int = 5,
        offset: int = 0,
        account_id: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Search indexed files matching keywords.
        Returns (list_of_results, total_matches).
        Matches all search tokens against file name, path, and category.
        Only searches across currently active accounts.
        """
        tokens = [t.strip().lower() for t in query.split() if t.strip()]
        if not tokens:
            return [], 0

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Base query: join files with accounts
            conditions = ["a.is_active = 1"]
            params: List[Any] = []

            if account_id is not None:
                conditions.append("f.account_id = ?")
                params.append(account_id)

            # Each token must match somewhere in file_name or file_path
            for token in tokens:
                conditions.append("(LOWER(f.file_name) LIKE ? OR LOWER(f.file_path) LIKE ? OR LOWER(f.category) LIKE ?)")
                like_term = f"%{token}%"
                params.extend([like_term, like_term, like_term])

            where_clause = " WHERE " + " AND ".join(conditions)

            # Count total matches
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM files f
                JOIN accounts a ON f.account_id = a.id
                {where_clause}
            """
            cursor.execute(count_sql, params)
            total_matches = cursor.fetchone()["total"]

            if total_matches == 0:
                return [], 0

            # Fetch paginated results ordered by relevance (exact match first, then size/name)
            select_sql = f"""
                SELECT
                    f.id,
                    f.account_id,
                    a.label as account_label,
                    f.fs_id,
                    f.file_name,
                    f.file_path,
                    f.file_size,
                    f.is_dir,
                    f.category,
                    f.share_url,
                    f.direct_url,
                    f.link_type,
                    f.md5,
                    f.updated_at
                FROM files f
                JOIN accounts a ON f.account_id = a.id
                {where_clause}
                ORDER BY
                    CASE WHEN LOWER(f.file_name) = ? THEN 0
                         WHEN LOWER(f.file_name) LIKE ? THEN 1
                         ELSE 2 END,
                    f.is_dir ASC,
                    f.file_size DESC
                LIMIT ? OFFSET ?
            """
            full_query = query.strip().lower()
            order_params = [full_query, f"{full_query}%"]
            final_params = params + order_params + [limit, offset]

            cursor.execute(select_sql, final_params)
            results = [dict(row) for row in cursor.fetchall()]

            return results, total_matches

    def get_file_by_id(self, file_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve single file by ID with account label."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.*, a.label as account_label
                FROM files f
                JOIN accounts a ON f.account_id = a.id
                WHERE f.id = ?
            """, (file_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # -------------------------------------------------------------------------
    # Bot & System Statistics
    # -------------------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        """Aggregate stats for /status command."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Accounts
            cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN is_active=1 THEN 1 ELSE 0 END) as active FROM accounts")
            acc_row = cursor.fetchone()
            total_accounts = acc_row["total"] or 0
            active_accounts = acc_row["active"] or 0

            # Files
            cursor.execute("SELECT COUNT(*) as total_files, SUM(file_size) as total_bytes FROM files")
            file_row = cursor.fetchone()
            total_files = file_row["total_files"] or 0
            total_bytes = file_row["total_bytes"] or 0

            # Categories
            cursor.execute("SELECT category, COUNT(*) as cnt FROM files GROUP BY category ORDER BY cnt DESC")
            categories = {row["category"]: row["cnt"] for row in cursor.fetchall()}

            # DB File Size
            db_size_bytes = 0
            if os.path.exists(self.db_path):
                db_size_bytes = os.path.getsize(self.db_path)

            return {
                "total_accounts": total_accounts,
                "active_accounts": active_accounts,
                "total_files": total_files,
                "total_bytes": total_bytes,
                "categories": categories,
                "db_size_bytes": db_size_bytes,
            }
