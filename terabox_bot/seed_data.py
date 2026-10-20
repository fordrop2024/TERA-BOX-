"""
Sample Dataset Seeder
=====================
Pre-populates the SQLite database with realistic mock TeraBox files across
multiple accounts so users can immediately test the Telegram bot without
real TeraBox accounts.
"""

from typing import Any, Dict, List
from .database import Database

SAMPLE_ACCOUNTS = [
    {
        "label": "Media-Vault-Alpha",
        "ndus": "mock_sample_ndus_cookie_alpha_9281734",
        "is_active": 1,
        "auth_status": "mock_connected"
    },
    {
        "label": "Cinema-Archive-Beta",
        "ndus": "mock_sample_ndus_cookie_beta_5510294",
        "is_active": 1,
        "auth_status": "mock_connected"
    },
    {
        "label": "DevOps-Software-HQ",
        "ndus": "mock_sample_ndus_cookie_gamma_1928374",
        "is_active": 1,
        "auth_status": "mock_connected"
    }
]

SAMPLE_FILES: List[Dict[str, Any]] = [
    # Movies / Video - Specifically including "Example Movie 1080p" as highlighted in the prompt!
    {
        "account_idx": 0,
        "fs_id": "1001",
        "file_name": "Example Movie 1080p BluRay x264 DTS-HD.mkv",
        "file_path": "/Movies/Example Movie/",
        "file_size": 2576980377,  # ~2.4 GB
        "category": "Video",
        "share_url": "https://terabox.com/s/1ExAmPlEmOvIe1080pKeyA",
        "link_type": "share",
        "md5": "e99a18c428cb38d5f260853678922e03"
    },
    {
        "account_idx": 1,
        "fs_id": "1002",
        "file_name": "Example Movie 1080p REMUX AVC TrueHD 7.1.mkv",
        "file_path": "/Archive/Movies/Remux/",
        "file_size": 18456123400,  # ~17.1 GB
        "category": "Video",
        "share_url": "https://terabox.com/s/1ExAmPlEmOvIeRemuxKeyB",
        "link_type": "share",
        "md5": "b10a8db164e0754105b7a99be72e3fe5"
    },
    {
        "account_idx": 1,
        "fs_id": "1003",
        "file_name": "Example Movie 720p WEB-DL x264 AAC.mp4",
        "file_path": "/Movies/Web-Rips/",
        "file_size": 943718400,  # ~900 MB
        "category": "Video",
        "share_url": "https://terabox.com/s/1ExAmPlEmOvIe720pKeyC",
        "link_type": "share",
        "md5": "c4ca4238a0b923820dcc509a6f75849b"
    },
    {
        "account_idx": 0,
        "fs_id": "1004",
        "file_name": "Example Movie English Subtitles Pack.zip",
        "file_path": "/Movies/Subtitles/",
        "file_size": 1258291,  # ~1.2 MB
        "category": "Archive",
        "share_url": "https://terabox.com/s/1ExAmPlESubsPackKeyD",
        "link_type": "share",
        "md5": "d41d8cd98f00b204e9800998ecf8427e"
    },
    {
        "account_idx": 1,
        "fs_id": "1005",
        "file_name": "Interstellar 2014 IMAX 1080p 10bit BluRay x265 HEVC.mkv",
        "file_path": "/Movies/SciFi/",
        "file_size": 3435973836,  # ~3.2 GB
        "category": "Video",
        "share_url": "https://terabox.com/s/1InterstellarImax1080pX",
        "link_type": "share",
        "md5": "9b7d8c0b5f1e8a2a7b3c4d5e6f7a8b9c"
    },
    {
        "account_idx": 1,
        "fs_id": "1006",
        "file_name": "Oppenheimer 2023 UHD 2160p HDR BluRay HEVC.mkv",
        "file_path": "/Movies/Drama/",
        "file_size": 24159191040,  # ~22.5 GB
        "category": "Video",
        "share_url": "https://terabox.com/s/1OppenheimerUHD2160pY",
        "link_type": "share",
        "md5": "8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d"
    },
    {
        "account_idx": 0,
        "fs_id": "1007",
        "file_name": "Spider-Man Across the Spider-Verse 1080p WEB.mkv",
        "file_path": "/Movies/Animation/",
        "file_size": 2899102924,  # ~2.7 GB
        "category": "Video",
        "share_url": "https://terabox.com/s/1SpiderManSpiderVerseZ",
        "link_type": "share",
        "md5": "7f6e5d4c3b2a1098fedcba9876543210"
    },

    # Software & Operating Systems
    {
        "account_idx": 2,
        "fs_id": "2001",
        "file_name": "ubuntu-24.04.1-desktop-amd64.iso",
        "file_path": "/OS_Images/Linux/",
        "file_size": 6116769792,  # ~5.7 GB
        "category": "Software",
        "share_url": "https://terabox.com/s/1Ubuntu2404DesktopIsoW",
        "link_type": "share",
        "md5": "2f4b8c9d0e1a2b3c4d5e6f7a8b9c0d1e"
    },
    {
        "account_idx": 2,
        "fs_id": "2002",
        "file_name": "Debian-12.5.0-netinst-x86_64.iso",
        "file_path": "/OS_Images/Linux/",
        "file_size": 655360000,  # ~625 MB
        "category": "Software",
        "share_url": "https://terabox.com/s/1DebianNetinst125IsoV",
        "link_type": "share",
        "md5": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d"
    },
    {
        "account_idx": 2,
        "fs_id": "2003",
        "file_name": "VSCode-Setup-x64-1.93.1.exe",
        "file_path": "/Software/DeveloperTools/",
        "file_size": 96468992,  # ~92 MB
        "category": "Software",
        "share_url": "https://terabox.com/s/1VSCodeSetupWin64U",
        "link_type": "share",
        "md5": "3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a"
    },
    {
        "account_idx": 2,
        "fs_id": "2004",
        "file_name": "DockerDesktop-Windows-x64.exe",
        "file_path": "/Software/Containers/",
        "file_size": 629145600,  # ~600 MB
        "category": "Software",
        "share_url": "https://terabox.com/s/1DockerDesktopInstallerT",
        "link_type": "share",
        "md5": "4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b"
    },

    # Courses & Learning Material
    {
        "account_idx": 0,
        "fs_id": "3001",
        "file_name": "Python Machine Learning Masterclass 2026.zip",
        "file_path": "/Courses/Python/",
        "file_size": 5242880000,  # ~4.8 GB
        "category": "Archive",
        "share_url": "https://terabox.com/s/1PythonMLMasterclassZipS",
        "link_type": "share",
        "md5": "5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c"
    },
    {
        "account_idx": 0,
        "fs_id": "3002",
        "file_name": "Full Stack Web Development with React and Node.pdf",
        "file_path": "/Books/Programming/",
        "file_size": 31457280,  # ~30 MB
        "category": "Document",
        "share_url": "https://terabox.com/s/1ReactNodeFullStackBookR",
        "link_type": "share",
        "md5": "6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d"
    },
    {
        "account_idx": 2,
        "fs_id": "3003",
        "file_name": "Computer Networking A Top-Down Approach 8th.pdf",
        "file_path": "/Books/Networking/",
        "file_size": 47185920,  # ~45 MB
        "category": "Document",
        "share_url": "https://terabox.com/s/1NetworkingTopDown8thPdfQ",
        "link_type": "share",
        "md5": "7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e"
    },

    # Audio & FLAC Music
    {
        "account_idx": 1,
        "fs_id": "4001",
        "file_name": "Hans Zimmer - Live in Prague 24bit-96kHz FLAC.zip",
        "file_path": "/Music/FLAC/Hans Zimmer/",
        "file_size": 1932735283,  # ~1.8 GB
        "category": "Audio",
        "share_url": "https://terabox.com/s/1HansZimmerLivePragueFlacP",
        "link_type": "share",
        "md5": "8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f"
    },
    {
        "account_idx": 1,
        "fs_id": "4002",
        "file_name": "Cyberpunk 2077 Original Soundtrack 320kbps MP3.zip",
        "file_path": "/Music/OST/",
        "file_size": 471859200,  # ~450 MB
        "category": "Audio",
        "share_url": "https://terabox.com/s/1CyberpunkOSTMp3O",
        "link_type": "share",
        "md5": "9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a"
    }
]


def seed_database(db: Database, force: bool = False) -> None:
    """Populate database with sample accounts and files if empty or forced."""
    accounts = db.get_accounts()
    if accounts and not force:
        # Already has data
        return

    # Create sample accounts
    created_account_ids: List[int] = []
    for acc in SAMPLE_ACCOUNTS:
        acc_id = db.add_account(
            label=acc["label"],
            ndus_cookie=acc["ndus"],
            is_active=acc["is_active"]
        )
        # Update mock status
        db.update_account_status(acc_id, auth_status=acc["auth_status"], total_files=0)
        created_account_ids.append(acc_id)

    # Insert sample files
    files_per_acc: Dict[int, int] = {aid: 0 for aid in created_account_ids}
    for file_info in SAMPLE_FILES:
        acc_id = created_account_ids[file_info["account_idx"]]
        db.upsert_file(
            account_id=acc_id,
            fs_id=file_info["fs_id"],
            file_name=file_info["file_name"],
            file_path=file_info["file_path"],
            file_size=file_info["file_size"],
            is_dir=0,
            category=file_info["category"],
            share_url=file_info["share_url"],
            link_type=file_info["link_type"],
            md5=file_info["md5"]
        )
        files_per_acc[acc_id] += 1

    # Update account file counts
    for aid, count in files_per_acc.items():
        db.update_account_status(aid, auth_status="mock_connected", total_files=count)
