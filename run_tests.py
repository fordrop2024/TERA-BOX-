#!/usr/bin/env python3
"""
Comprehensive Test Suite for TeraBox Search Bot
================================================
Verifies SQLite database operations, sample dataset indexing, keyword search
scoring, multi-account isolation, admin security, and message formatters.
Uses standard Python unittest (no external dependencies required).
"""

import os
import shutil
import tempfile
import unittest

from terabox_bot.config import BotConfig
from terabox_bot.database import Database
from terabox_bot.seed_data import seed_database
from terabox_bot.terabox.client import TeraBoxClient
from terabox_bot.terabox.account_manager import AccountManager
from terabox_bot.bot.handlers import BotHandlerService
from terabox_bot.bot.formatters import format_bytes, get_category_emoji, format_search_results


class TestTeraBoxSearchBot(unittest.TestCase):
    """Test suite covering core bot workflows."""

    def setUp(self):
        # Create isolated temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.test_dir, "test_search.db")
        self.db = Database(self.db_path)
        # Seed test data
        seed_database(self.db, force=True)
        self.acc_manager = AccountManager(self.db)
        self.handler_service = BotHandlerService(self.db, self.acc_manager)
        self.admin_id = 999888777
        BotConfig.ADMIN_TELEGRAM_ID = self.admin_id

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_database_initialization_and_seeding(self):
        """Verify database tables and seeded records."""
        accounts = self.db.get_accounts()
        self.assertGreaterEqual(len(accounts), 3, "Expected at least 3 seeded accounts")

        stats = self.db.get_stats()
        self.assertGreaterEqual(stats["total_files"], 10, "Expected at least 10 seeded files")
        self.assertGreater(stats["total_bytes"], 1000000, "Seeded files should have realistic size")

    def test_search_example_movie_1080p(self):
        """Test specific search query mentioned in prompt: 'Example Movie 1080p'."""
        results, total = self.db.search_files("Example Movie 1080p", limit=5, offset=0)
        self.assertGreaterEqual(total, 1, "Should find 'Example Movie 1080p'")

        found_names = [r["file_name"] for r in results]
        self.assertTrue(
            any("Example Movie 1080p" in name for name in found_names),
            f"Expected 'Example Movie 1080p' in results, got {found_names}"
        )

        # First result should have valid share URL and account label
        first = results[0]
        self.assertTrue(first["share_url"].startswith("https://terabox.com/s/"))
        self.assertIn("account_label", first)
        self.assertEqual(first["link_type"], "share")

    def test_case_insensitive_and_token_search(self):
        """Search should be case-insensitive and match individual tokens."""
        lower_res, lower_tot = self.db.search_files("example movie", limit=5)
        upper_res, upper_tot = self.db.search_files("EXAMPLE MOVIE", limit=5)
        mixed_res, mixed_tot = self.db.search_files("ExAmPlE MoViE", limit=5)

        self.assertEqual(lower_tot, upper_tot)
        self.assertEqual(lower_tot, mixed_tot)
        self.assertGreaterEqual(lower_tot, 2)

    def test_pagination(self):
        """Test pagination limit and offset."""
        results_p1, total = self.db.search_files("Example", limit=2, offset=0)
        results_p2, _ = self.db.search_files("Example", limit=2, offset=2)

        self.assertEqual(len(results_p1), 2)
        if total > 2:
            self.assertGreaterEqual(len(results_p2), 1)
            # Ensure different items are returned
            ids_p1 = {r["id"] for r in results_p1}
            ids_p2 = {r["id"] for r in results_p2}
            self.assertTrue(ids_p1.isdisjoint(ids_p2), "Pages must contain distinct items")

    def test_multi_account_isolation_and_toggling(self):
        """Test enabling and disabling accounts affects search results."""
        accounts = self.db.get_accounts()
        acc_alpha = next(a for a in accounts if a["label"] == "Media-Vault-Alpha")

        # Initial search includes Alpha items
        initial_res, initial_tot = self.db.search_files("Subtitles", limit=5)
        self.assertGreaterEqual(initial_tot, 1)

        # Disable account Alpha
        self.db.toggle_account(acc_alpha["id"], is_active=False)

        # Disabled account's files must not appear
        after_res, after_tot = self.db.search_files("Subtitles", limit=5)
        self.assertEqual(after_tot, 0, "Files from disabled accounts must not be returned")

        # Re-enable
        self.db.toggle_account(acc_alpha["id"], is_active=True)
        restored_res, restored_tot = self.db.search_files("Subtitles", limit=5)
        self.assertEqual(restored_tot, initial_tot)

    def test_admin_authorization(self):
        """Test that regular users cannot access administrative commands."""
        regular_user_id = 111222333

        # Non-admin /status
        status_text, _ = self.handler_service.handle_status(regular_user_id)
        self.assertIn("Access Denied", status_text)

        # Non-admin /accounts
        accounts_text, _ = self.handler_service.handle_accounts(regular_user_id)
        self.assertIn("Access Denied", accounts_text)

        # Non-admin /sync
        sync_text, _ = self.handler_service.handle_sync(regular_user_id)
        self.assertIn("Access Denied", sync_text)

        # Admin /status
        admin_status, _ = self.handler_service.handle_status(self.admin_id)
        self.assertIn("Admin View", admin_status)
        self.assertIn("Connected Accounts", admin_status)

    def test_category_detection(self):
        """Test file extension categorization logic."""
        self.assertEqual(TeraBoxClient.detect_category("test.mkv"), "Video")
        self.assertEqual(TeraBoxClient.detect_category("song.flac"), "Audio")
        self.assertEqual(TeraBoxClient.detect_category("installer.iso"), "Software")
        self.assertEqual(TeraBoxClient.detect_category("notes.pdf"), "Document")
        self.assertEqual(TeraBoxClient.detect_category("archive.7z"), "Archive")
        self.assertEqual(TeraBoxClient.detect_category("anything", is_dir=1), "Folder")

    def test_formatters(self):
        """Test byte formatting and HTML escaping."""
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1048576), "1.00 MB")
        self.assertEqual(format_bytes(1073741824), "1.00 GB")
        self.assertEqual(format_bytes(0), "Unknown size")

        self.assertEqual(get_category_emoji("video"), "🎬")
        self.assertEqual(get_category_emoji("software"), "💾")

        # HTML injection protection
        results, total = self.db.search_files("Example", limit=1)
        output = format_search_results("<script>alert(1)</script>", results, total, 1, 5)
        self.assertNotIn("<script>", output)
        self.assertIn("&lt;script&gt;", output)

    def test_mock_account_verification(self):
        """Verify mock account verification works safely."""
        client = TeraBoxClient(ndus_cookie="mock_test_cookie")
        is_valid, details = client.verify_connection()
        self.assertTrue(is_valid)
        self.assertTrue(details.get("is_mock"))

        # Empty cookie must fail verification
        empty_client = TeraBoxClient(ndus_cookie="")
        is_valid_empty, details_empty = empty_client.verify_connection()
        self.assertFalse(is_valid_empty)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" Running TeraBox Search Bot Test Suite")
    print("=" * 60)
    unittest.main(verbosity=2)
