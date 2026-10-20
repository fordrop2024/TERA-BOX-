# TeraBox Search Bot

A production-grade, zero-cost **Telegram Bot** built in Python that enables users to search indexed files across authorized, connected TeraBox cloud storage accounts and retrieve valid file links directly within Telegram.

---

## ⚡ Important Architecture Note

* **Direct Telegram Experience:** This application runs as a real Telegram bot. Users interact with it solely inside their official Telegram desktop, mobile, or web client.
* **Zero Cost:** Requires no paid AI APIs, no monthly subscriptions, and no paid hosting. You can run it on your own local PC or any free/cheap Linux VPS.
* **Local Backend Requirement:** The bot will respond in Telegram only while the Python backend script (`main.py`) is running on your machine or server.
* **TeraBox Link Limitation:** TeraBox official share links (`https://terabox.com/s/...`) open in the web browser or official TeraBox app so users can preview, stream, or save files to their cloud drive. Direct CDN streaming without an active login session is restricted by TeraBox's anti-bot protections.

---

## 🚀 Quick Setup Guide (Step-by-Step)

### Step 1: Create Your Telegram Bot via @BotFather

1. Open your Telegram app and search for the official account **`@BotFather`** (verified checkmark).
2. Click **Start** or send the command:
   ```text
   /newbot
   ```
3. BotFather will ask for a **Name** for your bot (e.g., `My TeraBox Searcher`).
4. Next, choose a unique **Username** ending in `bot` (e.g., `my_terabox_indexer_bot`).
5. BotFather will generate an API Token in this format:
   ```text
   1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ123456789
   ```
6. **Save this token** — you will paste it into your `.env` file.

---

### Step 2: Find Your Telegram User ID (For Administrator Security)

1. In Telegram, search for **`@userinfobot`** and send any message (or `/start`).
2. The bot will instantly reply with your numeric **Id** (e.g., `123456789`).
3. This ID will be assigned to `ADMIN_TELEGRAM_ID` in your `.env` file.
   * *Only this ID can run management commands like `/status`, `/accounts`, `/addaccount`, and `/sync`.*

---

### Step 3: Windows Quickstart (PowerShell)

Open **PowerShell** in the project folder and follow these commands:

```powershell
# 1. Allow running scripts in the current PowerShell session (if blocked)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Copy the sample environment file to .env
Copy-Item .env.example .env

# 3. Open .env in Notepad to insert your bot token and admin ID
notepad .env
```

In `.env`, set:
```ini
TELEGRAM_BOT_TOKEN="1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ123456789"
ADMIN_TELEGRAM_ID="123456789"
ENABLE_SAMPLE_DATA="true"
```

Then create your virtual environment and launch:

```powershell
# 4. Create virtual environment
python -m venv venv

# 5. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 6. Install dependencies
pip install -r requirements.txt

# 7. (Optional) Run the automated test suite to verify everything
python run_tests.py

# 8. Start the bot!
python main.py
```

*Alternatively, double-click **`start_bot.bat`** or run **`.\start_bot.ps1`** for automated one-click startup!*

---

### Linux / macOS Quickstart

```bash
# 1. Clone/Navigate to folder
cd terabox_bot

# 2. Copy environment template
cp .env.example .env

# 3. Edit settings
nano .env

# 4. Setup Python environment
python3 -m venv venv
source venv/bin/activate

# 5. Install libraries
pip install -r requirements.txt

# 6. Run test suite
python3 run_tests.py

# 7. Start bot
python3 main.py
```

---

## 🧪 Testing Search Without Real TeraBox Accounts

Out of the box, `ENABLE_SAMPLE_DATA="true"` initializes an indexed SQLite database containing **16 realistic sample files** (movies, operating systems, programming courses, music) across 3 sample accounts.

Once your bot is running, open Telegram and test these queries:
* `Example Movie 1080p`
* `Example Movie`
* `Ubuntu 24.04`
* `Python Masterclass`
* `Hans Zimmer FLAC`

Each result includes:
* 📄 Full file title & category emoji badge (🎬, 💾, 📚, 📦, 🎵).
* 💾 File size in MB/GB.
* 🏷️ Source TeraBox account label.
* 🔗 Clickable inline button: **`[ 🔗 Open File on TeraBox ]`**
* 📄 Interactive pagination buttons: `[ ◀ Prev ]`, `[ 1/3 ]`, `[ Next ▶ ]`.

---

## 🔗 How to Connect Real TeraBox Accounts

To index files from real TeraBox accounts, extract the account's session cookie:

1. Open your browser and go to [https://www.terabox.com](https://www.terabox.com).
2. Log in to your TeraBox account.
3. Press **F12** to open Developer Tools.
4. Go to the **Application** tab (Chrome/Edge) or **Storage** tab (Firefox).
5. In the left panel, expand **Cookies** → select `https://www.terabox.com`.
6. Find the cookie named **`ndus`** and copy its string value.

### Method A: Add via Telegram (Admin Command)
In Telegram, message your bot:
```text
/addaccount MyCloud ndus_cookie_value_here
```
The bot will test authentication with TeraBox servers, verify credentials, and register the account.

### Method B: Configure in `.env`
You can configure a default account in `.env`:
```ini
TERABOX_ACCOUNT_1_LABEL="Primary-Cloud"
TERABOX_ACCOUNT_1_NDUS="your_ndus_cookie_here"
```

Once added, run:
```text
/sync
```
The bot will crawl the cloud directories and index all files into SQLite.

---

## 📱 Telegram Commands Reference

### User Commands (Available to Everyone)
| Command | Description |
| :--- | :--- |
| `/start` | Welcome greeting, quick tips, and search syntax. |
| `/help` | Detailed guide on search terms, filters, and link types. |
| `/search <term>` | Search indexed files (e.g. `/search Example Movie 1080p`). |
| *(Any text)* | Sending any message (without `/`) automatically triggers a file search. |

### Administrator Commands (Protected by `ADMIN_TELEGRAM_ID`)
| Command | Description |
| :--- | :--- |
| `/status` | View bot uptime, database storage, active accounts, and file breakdown. |
| `/accounts` | List configured accounts with status badges and quick action buttons. |
| `/addaccount <label> <ndus>` | Add and verify a new TeraBox account connection. |
| `/toggleaccount <id>` | Enable or disable an account without losing indexed data. |
| `/delaccount <id>` | Remove an account and purge its files from the index. |
| `/sync [label]` | Re-index cloud files into the local SQLite database. |

---

## 🗄️ Database Architecture

The SQLite database (`data/terabox_search.db`) contains two primary tables:

1. **`accounts`**:
   * `id`, `label`, `ndus_cookie`, `is_active`, `auth_status`, `total_files`, `last_synced_at`, `created_at`.
2. **`files`**:
   * `id`, `account_id`, `fs_id`, `file_name`, `file_path`, `file_size`, `category`, `share_url`, `direct_url`, `link_type`, `md5`, `updated_at`.
   * Indexes on `file_name`, `account_id`, and `category`.
   * Tokenized multi-word search algorithm ranking exact matches and matching token sets.

---

## 🛡️ Security Best Practices

1. **Keep `.env` Private:** Never commit `.env` or share your `TELEGRAM_BOT_TOKEN` or `ndus` cookies.
2. **Admin Isolation:** Only the Telegram ID set in `ADMIN_TELEGRAM_ID` can trigger sync or view system configuration.
3. **No Credential Leakage:** Sensitive cookies are never displayed to regular users in the Telegram chat.
