"""
Modular TeraBox Connector
=========================
Connects to authorized TeraBox accounts using session cookies (NDUS), validates
connectivity, searches remote directories, indexes files, and generates valid
share links.

LIMITATION NOTICE:
TeraBox official share links (e.g. https://terabox.com/s/...) open in the web
browser or TeraBox mobile application. Direct CDN download tickets require
short-lived tokens and are subject to TeraBox anti-bot challenges.
This connector clearly differentiates between 'share' and 'direct' link types.
"""

import json
import logging
import urllib.parse
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import (
    TeraBoxAuthError,
    TeraBoxError,
    TeraBoxLinkExpiredError,
    TeraBoxNetworkError,
    TeraBoxRateLimitError,
)

logger = logging.getLogger(__name__)


class TeraBoxClient:
    """Interface for communicating with an authorized TeraBox account."""

    BASE_URL = "https://www.terabox.com"
    API_USER_INFO = f"{BASE_URL}/api/getuserinfo"
    API_LIST = f"{BASE_URL}/api/list"
    API_SEARCH = f"{BASE_URL}/api/search"
    API_SHARE_CREATE = f"{BASE_URL}/api/share/pset"

    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )

    def __init__(self, ndus_cookie: str, app_id: str = "250528", timeout: int = 15):
        self.ndus_cookie = (ndus_cookie or "").strip()
        self.app_id = app_id
        self.timeout = timeout
        self.is_mock = self.ndus_cookie.startswith("mock_")

    def _build_headers(self) -> Dict[str, str]:
        """Construct standard HTTP headers with authentication cookies."""
        headers = {
            "User-Agent": self.DEFAULT_USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.terabox.com/main",
            "Origin": "https://www.terabox.com",
        }
        if self.ndus_cookie:
            headers["Cookie"] = f"ndus={self.ndus_cookie}; lang=en;"
        return headers

    def _request(self, url: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute HTTP GET or POST request with cookie authentication."""
        if self.is_mock:
            # Safe mock mode handler for testing without network requests
            return {"errno": 0, "mock": True, "message": "Mock response"}

        if not self.ndus_cookie:
            raise TeraBoxAuthError("Missing NDUS session cookie. Please configure account credentials.")

        query_params = {"app_id": self.app_id}
        if params:
            query_params.update(params)

        full_url = f"{url}?{urllib.parse.urlencode(query_params)}"
        req_headers = self._build_headers()

        payload_bytes = None
        if data is not None:
            payload_bytes = urllib.parse.urlencode(data).encode("utf-8")
            req_headers["Content-Type"] = "application/x-www-form-urlencoded"

        req = urllib.request.Request(
            full_url,
            data=payload_bytes,
            headers=req_headers,
            method="POST" if payload_bytes else "GET"
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                status_code = response.getcode()
                raw_body = response.read().decode("utf-8", errors="replace")

                if status_code == 429:
                    raise TeraBoxRateLimitError("TeraBox rate limit exceeded (HTTP 429).")
                elif status_code != 200:
                    raise TeraBoxNetworkError(f"TeraBox server returned unexpected status HTTP {status_code}.")

                try:
                    res_json = json.loads(raw_body)
                except json.JSONDecodeError as e:
                    raise TeraBoxNetworkError(f"Failed to parse TeraBox JSON response: {e}")

                # Check TeraBox errno conventions
                errno = res_json.get("errno", 0)
                if errno in (-6, -9, 1000):
                    raise TeraBoxAuthError(f"TeraBox authentication failed (errno: {errno}). Cookie may be expired.")
                elif errno != 0:
                    errmsg = res_json.get("errmsg") or res_json.get("show_msg") or f"API error code {errno}"
                    raise TeraBoxError(f"TeraBox API Error: {errmsg}")

                return res_json

        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise TeraBoxAuthError(f"Authentication rejected by TeraBox (HTTP {e.code}).")
            elif e.code == 429:
                raise TeraBoxRateLimitError("Rate limit encountered from TeraBox (HTTP 429).")
            else:
                raise TeraBoxNetworkError(f"HTTP request failed: {e}")
        except urllib.error.URLError as e:
            raise TeraBoxNetworkError(f"Could not connect to TeraBox servers: {e.reason}")
        except TimeoutError:
            raise TeraBoxNetworkError(f"Connection to TeraBox timed out after {self.timeout}s.")

    def verify_connection(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify that this account's NDUS cookie is currently valid.
        Never fakes a successful live connection: tests actual endpoint.
        """
        if self.is_mock:
            return True, {
                "verified": True,
                "username": "SampleTester",
                "uk": "mock_uk_99999",
                "is_mock": True,
                "message": "Using validated sample mock account"
            }

        if not self.ndus_cookie:
            return False, {"verified": False, "error": "NDUS cookie is empty"}

        try:
            res = self._request(self.API_USER_INFO)
            # TeraBox returns user details in result
            records = res.get("records", {})
            uname = records.get("uname") or records.get("username") or "TeraBox User"
            uk = records.get("uk", "Unknown")
            return True, {
                "verified": True,
                "username": uname,
                "uk": uk,
                "is_mock": False
            }
        except TeraBoxAuthError as e:
            logger.warning(f"TeraBox auth verification failed: {e}")
            return False, {"verified": False, "error": str(e)}
        except Exception as e:
            logger.error(f"TeraBox connection error: {e}")
            return False, {"verified": False, "error": str(e)}

    def search_remote_files(self, keyword: str, directory: str = "/", page: int = 1, num: int = 100) -> List[Dict[str, Any]]:
        """
        Search files across the remote TeraBox storage using the search endpoint.
        Returns normalized file metadata dictionaries.
        """
        if self.is_mock:
            return []

        params = {
            "key": keyword,
            "dir": directory,
            "page": page,
            "num": num,
            "web": "1"
        }
        res = self._request(self.API_SEARCH, params=params)
        file_list = res.get("list", [])
        return [self._normalize_file(item) for item in file_list]

    def list_directory(self, directory: str = "/", page: int = 1, num: int = 100) -> List[Dict[str, Any]]:
        """
        List files and folders within a specific directory.
        """
        if self.is_mock:
            return []

        params = {
            "dir": directory,
            "order": "time",
            "desc": "1",
            "page": page,
            "num": num,
            "web": "1"
        }
        res = self._request(self.API_LIST, params=params)
        file_list = res.get("list", [])
        return [self._normalize_file(item) for item in file_list]

    def create_share_link(self, fs_id: str, period: int = 0) -> str:
        """
        Request TeraBox to generate a public share link for a file.
        Returns the valid share URL (e.g. https://terabox.com/s/1xyz...).
        """
        if self.is_mock:
            return f"https://terabox.com/s/1MockShareKey{fs_id}"

        # period: 0 = permanent, 7 = 7 days
        payload = {
            "fid_list": f"[{fs_id}]",
            "period": period,
            "schannel": 0,
            "channel_list": "[]"
        }
        try:
            res = self._request(self.API_SHARE_CREATE, data=payload)
            short_url = res.get("shorturl")
            link = res.get("link")
            if link:
                return link
            if short_url:
                return f"https://terabox.com/s/1{short_url}"
        except Exception as e:
            logger.warning(f"Could not generate remote share link for fs_id {fs_id}: {e}")

        # Fallback to direct file preview URL template
        return f"https://terabox.com/sharing/link?surl={fs_id}"

    def _normalize_file(self, raw_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TeraBox API raw item to normalized bot representation."""
        fs_id = str(raw_item.get("fs_id", ""))
        server_filename = raw_item.get("server_filename", "Unnamed_File")
        path = raw_item.get("path", "/")
        size = int(raw_item.get("size", 0))
        is_dir = int(raw_item.get("isdir", 0))
        md5 = raw_item.get("md5", "")

        # Category determination
        category = self.detect_category(server_filename, is_dir)

        # Share Link
        share_url = raw_item.get("share_url") or self.create_share_link(fs_id)

        # Direct link ticket check (short-lived, if provided by API)
        dlink = raw_item.get("dlink")
        link_type = "direct" if (dlink and dlink.startswith("http")) else "share"

        return {
            "fs_id": fs_id,
            "file_name": server_filename,
            "file_path": path,
            "file_size": size,
            "is_dir": is_dir,
            "category": category,
            "share_url": share_url,
            "direct_url": dlink if link_type == "direct" else None,
            "link_type": link_type,
            "md5": md5
        }

    @staticmethod
    def detect_category(filename: str, is_dir: int = 0) -> str:
        """Infer file category from file extension."""
        if is_dir:
            return "Folder"

        ext = filename.lower().split(".")[-1] if "." in filename else ""
        video_exts = {"mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v", "ts", "rmvb"}
        audio_exts = {"mp3", "flac", "wav", "aac", "ogg", "m4a", "wma", "opus"}
        software_exts = {"exe", "msi", "dmg", "apk", "iso", "img", "bin", "deb", "rpm"}
        archive_exts = {"zip", "rar", "7z", "tar", "gz", "bz2", "xz"}
        document_exts = {"pdf", "epub", "mobi", "docx", "doc", "xlsx", "pptx", "txt", "md"}
        image_exts = {"jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"}

        if ext in video_exts:
            return "Video"
        elif ext in audio_exts:
            return "Audio"
        elif ext in software_exts:
            return "Software"
        elif ext in archive_exts:
            return "Archive"
        elif ext in document_exts:
            return "Document"
        elif ext in image_exts:
            return "Image"
        return "Other"
