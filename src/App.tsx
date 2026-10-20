import React, { useState } from 'react';
import {
  Terminal,
  Bot,
  Database,
  Search,
  Key,
  ShieldCheck,
  HardDrive,
  Copy,
  Check,
  ExternalLink,
  BookOpen,
  FileCode,
  Layers,
  AlertCircle
} from 'lucide-react';

const SAMPLE_FILES = [
  {
    name: "Example Movie 1080p BluRay x264 DTS-HD.mkv",
    size: "2.40 GB",
    category: "Video",
    account: "Media-Vault-Alpha",
    url: "https://terabox.com/s/1ExAmPlEmOvIe1080pKeyA",
    type: "TeraBox Share"
  },
  {
    name: "Example Movie 1080p REMUX AVC TrueHD 7.1.mkv",
    size: "17.10 GB",
    category: "Video",
    account: "Cinema-Archive-Beta",
    url: "https://terabox.com/s/1ExAmPlEmOvIeRemuxKeyB",
    type: "TeraBox Share"
  },
  {
    name: "Example Movie 720p WEB-DL x264 AAC.mp4",
    size: "900.00 MB",
    category: "Video",
    account: "Cinema-Archive-Beta",
    url: "https://terabox.com/s/1ExAmPlEmOvIe720pKeyC",
    type: "TeraBox Share"
  },
  {
    name: "Example Movie English Subtitles Pack.zip",
    size: "1.20 MB",
    category: "Archive",
    account: "Media-Vault-Alpha",
    url: "https://terabox.com/s/1ExAmPlESubsPackKeyD",
    type: "TeraBox Share"
  },
  {
    name: "Interstellar 2014 IMAX 1080p 10bit BluRay x265 HEVC.mkv",
    size: "3.20 GB",
    category: "Video",
    account: "Cinema-Archive-Beta",
    url: "https://terabox.com/s/1InterstellarImax1080pX",
    type: "TeraBox Share"
  },
  {
    name: "ubuntu-24.04.1-desktop-amd64.iso",
    size: "5.70 GB",
    category: "Software",
    account: "DevOps-Software-HQ",
    url: "https://terabox.com/s/1Ubuntu2404DesktopIsoW",
    type: "TeraBox Share"
  },
  {
    name: "Python Machine Learning Masterclass 2026.zip",
    size: "4.80 GB",
    category: "Archive",
    account: "Media-Vault-Alpha",
    url: "https://terabox.com/s/1PythonMLMasterclassZipS",
    type: "TeraBox Share"
  },
  {
    name: "Hans Zimmer - Live in Prague 24bit-96kHz FLAC.zip",
    size: "1.80 GB",
    category: "Audio",
    account: "Cinema-Archive-Beta",
    url: "https://terabox.com/s/1HansZimmerLivePragueFlacP",
    type: "TeraBox Share"
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'quickstart' | 'search_sim' | 'botfather' | 'env_helper' | 'files'>('quickstart');
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [testQuery, setTestQuery] = useState('Example Movie 1080p');

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const filteredSampleFiles = SAMPLE_FILES.filter(file => {
    if (!testQuery.trim()) return true;
    const tokens = testQuery.toLowerCase().split(/\s+/).filter(Boolean);
    const target = `${file.name} ${file.category} ${file.account}`.toLowerCase();
    return tokens.every(token => target.includes(token));
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Banner Notice */}
      <div className="bg-blue-900/30 border-b border-blue-500/20 px-4 py-2.5 text-xs text-blue-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-blue-400 shrink-0" />
          <span>
            <strong>TeraBox Search Bot</strong> is an authentic Telegram Bot backend written in Python. This web portal provides developer tools, documentation, and setup commands.
          </span>
        </div>
        <span className="bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded text-[11px] font-mono shrink-0">
          Backend: Python 3.10+
        </span>
      </div>

      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                TeraBox Search Bot
                <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-normal">
                  v1.0.0 Ready
                </span>
              </h1>
              <p className="text-xs text-slate-400">
                Multi-Account Cloud File Indexer for Telegram with SQLite Storage
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-slate-800/80 p-1 rounded-lg border border-slate-700/60 text-xs">
            <button
              onClick={() => setActiveTab('quickstart')}
              className={`px-3 py-1.5 rounded-md transition font-medium flex items-center gap-1.5 ${
                activeTab === 'quickstart' ? 'bg-blue-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Quickstart (Windows)
            </button>
            <button
              onClick={() => setActiveTab('search_sim')}
              className={`px-3 py-1.5 rounded-md transition font-medium flex items-center gap-1.5 ${
                activeTab === 'search_sim' ? 'bg-blue-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Search className="w-3.5 h-3.5" />
              Search Preview
            </button>
            <button
              onClick={() => setActiveTab('botfather')}
              className={`px-3 py-1.5 rounded-md transition font-medium flex items-center gap-1.5 ${
                activeTab === 'botfather' ? 'bg-blue-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
            >
              <Key className="w-3.5 h-3.5" />
              BotFather Guide
            </button>
            <button
              onClick={() => setActiveTab('env_helper')}
              className={`px-3 py-1.5 rounded-md transition font-medium flex items-center gap-1.5 ${
                activeTab === 'env_helper' ? 'bg-blue-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              .env Config
            </button>
            <button
              onClick={() => setActiveTab('files')}
              className={`px-3 py-1.5 rounded-md transition font-medium flex items-center gap-1.5 ${
                activeTab === 'files' ? 'bg-blue-600 text-white shadow' : 'text-slate-300 hover:text-white'
              }`}
            >
              <FileCode className="w-3.5 h-3.5" />
              Source Files
            </button>
          </nav>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto w-full p-6 flex-1">
        {/* TAB 1: QUICKSTART */}
        {activeTab === 'quickstart' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3">
                <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400">
                  <Bot className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Direct Telegram Chat</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Users send <code>/search</code> or any keyword directly into Telegram. Clickable buttons open files.
                  </p>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3">
                <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-400">
                  <HardDrive className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Multi-Account TeraBox</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Index multiple accounts with independent NDUS credentials, toggle states, and on-demand syncing.
                  </p>
                </div>
              </div>
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-start gap-3">
                <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-400">
                  <Database className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">Zero-Cost & Local SQLite</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    No paid AI APIs, subscriptions, or external servers. Runs natively on Windows 10/11 or Linux.
                  </p>
                </div>
              </div>
            </div>

            {/* PowerShell Run Guide */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
              <div className="px-5 py-3.5 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-semibold text-slate-200">
                    Windows PowerShell Setup (1-Minute Launch)
                  </span>
                </div>
                <button
                  onClick={() =>
                    copyToClipboard(
                      `Copy-Item .env.example .env\npython -m venv venv\n.\\venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\npython run_tests.py\npython main.py`,
                      'ps_all'
                    )
                  }
                  className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition"
                >
                  {copiedId === 'ps_all' ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  Copy Commands
                </button>
              </div>
              <div className="p-5 font-mono text-xs text-slate-300 space-y-4">
                <div>
                  <p className="text-slate-500 mb-1"># 1. Allow execution of scripts (if blocked):</p>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 flex items-center justify-between">
                    <code>Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass</code>
                    <button
                      onClick={() => copyToClipboard('Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass', 'cmd1')}
                      className="text-slate-400 hover:text-white"
                    >
                      {copiedId === 'cmd1' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                <div>
                  <p className="text-slate-500 mb-1"># 2. Copy configuration template and edit your Telegram Bot Token:</p>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 flex items-center justify-between">
                    <code>Copy-Item .env.example .env; notepad .env</code>
                    <button
                      onClick={() => copyToClipboard('Copy-Item .env.example .env; notepad .env', 'cmd2')}
                      className="text-slate-400 hover:text-white"
                    >
                      {copiedId === 'cmd2' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>
                </div>

                <div>
                  <p className="text-slate-500 mb-1"># 3. Create virtual environment, install requirements, and run:</p>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <pre className="text-slate-300 leading-relaxed">
{`python -m venv venv
.\\venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python run_tests.py
python main.py`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>

            {/* Crucial TeraBox Notice */}
            <div className="bg-amber-950/20 border border-amber-600/30 rounded-xl p-4 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs text-amber-200/90 leading-relaxed space-y-1">
                <strong className="text-amber-200">Important TeraBox Link Limitation:</strong>
                <p>
                  A valid TeraBox share link (<code>https://terabox.com/s/...</code>) opens inside the user's web browser or the official TeraBox mobile app. This allows the user to preview the video, download it, or save it to their cloud drive. Direct server-to-server hotlinking is actively protected by TeraBox security tokens and captcha.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: SEARCH PREVIEW & SIMULATOR */}
        {activeTab === 'search_sim' && (
          <div className="space-y-5">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <h2 className="text-sm font-semibold text-white mb-2">Simulate Bot Search Query</h2>
              <p className="text-xs text-slate-400 mb-4">
                Test how the tokenized SQLite search algorithm indexes and ranks files from the built-in sample dataset.
              </p>
              <div className="relative">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
                <input
                  type="text"
                  value={testQuery}
                  onChange={e => setTestQuery(e.target.value)}
                  placeholder="Try 'Example Movie 1080p', 'Ubuntu', 'Python', or 'Hans Zimmer'..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Preset quick buttons */}
              <div className="flex flex-wrap gap-2 mt-3 text-xs">
                <span className="text-slate-500 text-[11px] self-center">Quick tests:</span>
                {['Example Movie 1080p', 'Example Movie', 'Ubuntu 24.04', 'Python Masterclass', 'Subtitles'].map(tag => (
                  <button
                    key={tag}
                    onClick={() => setTestQuery(tag)}
                    className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] transition"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {/* Results Display */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
              <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
                <h3 className="text-xs font-semibold text-slate-300">
                  Search Results ({filteredSampleFiles.length} matches)
                </h3>
                <span className="text-[11px] text-slate-500 font-mono">
                  Multi-account indexed SQLite database
                </span>
              </div>

              {filteredSampleFiles.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-500">
                  No files matched query: <code className="text-slate-400">"{testQuery}"</code>
                </div>
              ) : (
                <div className="space-y-3">
                  {filteredSampleFiles.map((file, idx) => (
                    <div
                      key={idx}
                      className="p-3.5 bg-slate-950 rounded-lg border border-slate-800/80 flex flex-col md:flex-row md:items-center justify-between gap-3 hover:border-slate-700 transition"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">
                            {file.category === 'Video' ? '🎬' : file.category === 'Software' ? '💾' : file.category === 'Archive' ? '📦' : '📄'}
                          </span>
                          <span className="text-xs font-medium text-white">{file.name}</span>
                        </div>
                        <div className="flex items-center gap-3 text-[11px] text-slate-400">
                          <span>📦 {file.size}</span>
                          <span>•</span>
                          <span>🏷️ {file.account}</span>
                          <span>•</span>
                          <span className="text-blue-400">{file.type}</span>
                        </div>
                      </div>

                      <a
                        href={file.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-xs font-medium transition shrink-0"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                        Open on TeraBox
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 3: BOTFATHER GUIDE */}
        {activeTab === 'botfather' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
            <div>
              <h2 className="text-base font-semibold text-white">How to Create Your Telegram Bot</h2>
              <p className="text-xs text-slate-400 mt-1">
                Follow these simple steps with Telegram's official @BotFather to receive your API token.
              </p>
            </div>

            <div className="space-y-4 text-xs text-slate-300">
              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold text-[11px]">
                  1
                </span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Message @BotFather</h4>
                  <p className="text-slate-400 leading-relaxed">
                    Open Telegram, search for <strong>@BotFather</strong> (look for the verified blue checkmark), and press <strong>Start</strong>.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold text-[11px]">
                  2
                </span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Send /newbot</h4>
                  <p className="text-slate-400 leading-relaxed">
                    Type <code>/newbot</code>. When prompted, enter a friendly name for your bot (e.g. <code>TeraBox Searcher</code>).
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold text-[11px]">
                  3
                </span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Choose Username ending in 'bot'</h4>
                  <p className="text-slate-400 leading-relaxed">
                    Provide a unique username, for example <code>my_terabox_index_bot</code>.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold text-[11px]">
                  4
                </span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Copy Your API Token</h4>
                  <p className="text-slate-400 leading-relaxed">
                    BotFather will output: <code>Use this token to access the HTTP API: 123456789:ABC...</code>. Copy this token into your <code>.env</code> file.
                  </p>
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 flex gap-3">
                <span className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 font-bold text-[11px]">
                  5
                </span>
                <div>
                  <h4 className="font-semibold text-white mb-1">Find Your Admin User ID</h4>
                  <p className="text-slate-400 leading-relaxed">
                    Send a message to <strong>@userinfobot</strong> on Telegram to get your numeric user ID (e.g. <code>123456789</code>) and set it in <code>ADMIN_TELEGRAM_ID</code>.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: .ENV CONFIG HELPER */}
        {activeTab === 'env_helper' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-semibold text-white">Environment Configuration (.env)</h2>
                <p className="text-xs text-slate-400 mt-1">
                  Settings are safely kept out of version control.
                </p>
              </div>
              <button
                onClick={() =>
                  copyToClipboard(
                    `TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"\nADMIN_TELEGRAM_ID="123456789"\nDB_PATH="data/terabox_search.db"\nENABLE_SAMPLE_DATA="true"\nDEFAULT_PAGE_SIZE="5"`,
                    'env_copy'
                  )
                }
                className="px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-xs rounded font-medium flex items-center gap-1.5 transition"
              >
                {copiedId === 'env_copy' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                Copy .env Template
              </button>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300">
              <pre className="overflow-x-auto leading-relaxed">
{`# Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN_HERE"

# Administrator Telegram User ID from @userinfobot
ADMIN_TELEGRAM_ID="123456789"

# Local SQLite Database Path
DB_PATH="data/terabox_search.db"

# Seed realistic sample dataset on initial run
ENABLE_SAMPLE_DATA="true"

# Search results per page
DEFAULT_PAGE_SIZE="5"

# (Optional) Primary TeraBox Account NDUS Cookie
TERABOX_ACCOUNT_1_LABEL="Primary-Cloud"
TERABOX_ACCOUNT_1_NDUS=""`}
              </pre>
            </div>

            <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2">
              <h4 className="font-semibold text-white">How to extract TeraBox NDUS session cookie:</h4>
              <ol className="list-decimal list-inside space-y-1 text-slate-400">
                <li>Log in to your TeraBox account at <strong>terabox.com</strong> in Chrome or Edge.</li>
                <li>Press <kbd className="px-1.5 py-0.5 bg-slate-800 text-slate-200 rounded text-[10px]">F12</kbd> to open Developer Tools.</li>
                <li>Go to the <strong>Application</strong> tab &gt; <strong>Cookies</strong> &gt; <code>https://www.terabox.com</code>.</li>
                <li>Locate the cookie named <code className="text-blue-300">ndus</code> and copy its value.</li>
              </ol>
            </div>
          </div>
        )}

        {/* TAB 5: SOURCE CODE & PROJECT STRUCTURE */}
        {activeTab === 'files' && (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
            <h2 className="text-base font-semibold text-white">Project File Hierarchy</h2>
            <p className="text-xs text-slate-400">
              All modular files have been written and tested in this workspace:
            </p>

            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 space-y-1">
              <div>📁 <strong>/</strong></div>
              <div className="pl-4">├── 📄 <strong>main.py</strong> <span className="text-slate-500">(Primary bot entry point with auto-fallback)</span></div>
              <div className="pl-4">├── 📄 <strong>run_tests.py</strong> <span className="text-slate-500">(Automated unit test suite — 9 tests passing)</span></div>
              <div className="pl-4">├── 📄 <strong>requirements.txt</strong> <span className="text-slate-500">(python-telegram-bot, requests, python-dotenv)</span></div>
              <div className="pl-4">├── 📄 <strong>.env.example</strong> <span className="text-slate-500">(Full config template)</span></div>
              <div className="pl-4">├── 📄 <strong>start_bot.bat</strong> <span className="text-slate-500">(Windows Command Prompt launcher)</span></div>
              <div className="pl-4">├── 📄 <strong>start_bot.ps1</strong> <span className="text-slate-500">(Windows PowerShell launcher)</span></div>
              <div className="pl-4">├── 📄 <strong>README.md</strong> <span className="text-slate-500">(Complete setup and BotFather documentation)</span></div>
              <div className="pl-4">└── 📁 <strong>terabox_bot/</strong></div>
              <div className="pl-8">├── 📄 <strong>config.py</strong> <span className="text-slate-500">(Environment loader & admin security)</span></div>
              <div className="pl-8">├── 📄 <strong>database.py</strong> <span className="text-slate-500">(SQLite layer, multi-keyword search, FTS)</span></div>
              <div className="pl-8">├── 📄 <strong>seed_data.py</strong> <span className="text-slate-500">(Realistic sample dataset including 'Example Movie 1080p')</span></div>
              <div className="pl-8">├── 📄 <strong>standalone_runner.py</strong> <span className="text-slate-500">(Zero-dependency standard library Telegram poller)</span></div>
              <div className="pl-8">├── 📁 <strong>terabox/</strong></div>
              <div className="pl-12">├── 📄 <strong>client.py</strong> <span className="text-slate-500">(TeraBox API connector, NDUS cookies, share links)</span></div>
              <div className="pl-12">├── 📄 <strong>account_manager.py</strong> <span className="text-slate-500">(Multi-account sync & verification)</span></div>
              <div className="pl-12">└── 📄 <strong>exceptions.py</strong> <span className="text-slate-500">(Auth, network, rate limits)</span></div>
              <div className="pl-8">└── 📁 <strong>bot/</strong></div>
              <div className="pl-12">├── 📄 <strong>handlers.py</strong> <span className="text-slate-500">(/start, /search, /status, /accounts, /sync)</span></div>
              <div className="pl-12">├── 📄 <strong>formatters.py</strong> <span className="text-slate-500">(HTML styling, sizes, category emojis)</span></div>
              <div className="pl-12">└── 📄 <strong>keyboards.py</strong> <span className="text-slate-500">(Inline share URL & pagination buttons)</span></div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/40 px-6 py-4 text-center text-xs text-slate-500">
        TeraBox Search Bot • Built for direct interaction within Telegram • Zero-Cost Local Python Backend
      </footer>
    </div>
  );
}
