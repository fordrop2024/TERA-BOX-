"""
Multi-Account Manager
=====================
Coordinates synchronization, validation, and lifecycle management for
multiple connected TeraBox accounts.
"""

import logging
from typing import Any, Dict, List, Optional
from ..database import Database
from .client import TeraBoxClient
from .exceptions import TeraBoxAuthError, TeraBoxError

logger = logging.getLogger(__name__)


class AccountManager:
    """Manages multi-account synchronization and status checks."""

    def __init__(self, db: Database):
        self.db = db

    def get_client_for_account(self, account: Dict[str, Any]) -> TeraBoxClient:
        """Instantiate a TeraBoxClient for a stored account record."""
        return TeraBoxClient(
            ndus_cookie=account.get("ndus_cookie", ""),
            app_id=account.get("app_id", "250528")
        )

    def verify_account(self, account_id: int) -> Dict[str, Any]:
        """Test and record authentication status for an account."""
        account = self.db.get_account(account_id)
        if not account:
            return {"success": False, "error": f"Account ID {account_id} not found"}

        client = self.get_client_for_account(account)
        is_valid, details = client.verify_connection()

        status_str = "connected" if is_valid else "auth_failed"
        self.db.update_account_status(account_id, auth_status=status_str)
        return {
            "success": is_valid,
            "account_id": account_id,
            "label": account["label"],
            "details": details
        }

    def sync_account(self, account_id: int, max_depth: int = 3) -> Dict[str, Any]:
        """
        Index files from an account into the database.
        Traverses root directory up to max_depth and upserts items into SQLite.
        """
        account = self.db.get_account(account_id)
        if not account:
            return {"success": False, "error": "Account not found"}

        if not account["is_active"]:
            return {"success": False, "error": f"Account '{account['label']}' is currently disabled"}

        client = self.get_client_for_account(account)

        # In mock accounts, files are already seeded
        if client.is_mock:
            files_count = len(self.db.search_files("", limit=1000, account_id=account_id)[0])
            self.db.update_account_status(account_id, auth_status="mock_connected", total_files=files_count)
            return {
                "success": True,
                "label": account["label"],
                "total_indexed": files_count,
                "is_mock": True,
                "message": f"Sample mock account '{account['label']}' active with {files_count} indexed items."
            }

        # Validate connection first
        is_valid, details = client.verify_connection()
        if not is_valid:
            self.db.update_account_status(account_id, auth_status="auth_failed")
            return {
                "success": False,
                "label": account["label"],
                "error": details.get("error", "Authentication failed. Check your NDUS cookie.")
            }

        indexed_count = 0
        directories_to_crawl = ["/"]
        visited_dirs = set()

        try:
            depth = 0
            while directories_to_crawl and depth < max_depth:
                current_batch = directories_to_crawl
                directories_to_crawl = []
                depth += 1

                for directory in current_batch:
                    if directory in visited_dirs:
                        continue
                    visited_dirs.add(directory)

                    page = 1
                    while True:
                        items = client.list_directory(directory=directory, page=page, num=100)
                        if not items:
                            break

                        for item in items:
                            if item["is_dir"]:
                                dir_path = f"{item['file_path'].rstrip('/')}/{item['file_name']}"
                                if dir_path not in visited_dirs:
                                    directories_to_crawl.append(dir_path)
                            else:
                                self.db.upsert_file(
                                    account_id=account_id,
                                    fs_id=item["fs_id"],
                                    file_name=item["file_name"],
                                    file_path=item["file_path"],
                                    file_size=item["file_size"],
                                    is_dir=0,
                                    category=item["category"],
                                    share_url=item["share_url"],
                                    direct_url=item["direct_url"],
                                    link_type=item["link_type"],
                                    md5=item["md5"]
                                )
                                indexed_count += 1

                        if len(items) < 100:
                            break
                        page += 1

            self.db.update_account_status(account_id, auth_status="connected", total_files=indexed_count)
            return {
                "success": True,
                "label": account["label"],
                "total_indexed": indexed_count,
                "is_mock": False
            }

        except TeraBoxAuthError as e:
            self.db.update_account_status(account_id, auth_status="auth_failed")
            return {"success": False, "label": account["label"], "error": f"Auth error during sync: {e}"}
        except Exception as e:
            logger.exception("Sync failed unexpectedly")
            return {"success": False, "label": account["label"], "error": str(e)}

    def sync_all_accounts(self) -> List[Dict[str, Any]]:
        """Trigger sync on all active accounts."""
        accounts = self.db.get_accounts(active_only=True)
        results = []
        for acc in accounts:
            res = self.sync_account(acc["id"])
            results.append(res)
        return results
