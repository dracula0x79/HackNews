
---

# HackNews

<img width="1024" height="1024" alt="unnamed" src="https://github.com/user-attachments/assets/e9f0dabf-a4db-4102-8265-2f36fdc7d090" />

A simple Python tracker that collects **today’s** hacking/security news from popular RSS feeds, Reddit, and Twitter hashtags, ranks and classifies them, and sends plain-text notifications to Telegram and Discord. Designed to run automatically (e.g., via Task Scheduler) and safe for defensive OSINT use.

---

## Features

* Collects news published **today** (X /timezone) from multiple RSS feeds + Reddit/Twitter hashtags.
* Ranks and classifies items (technique, attack, apt, security\_tech, vulnerability, other).
* Avoids duplicate notifications using `data/seen.json` (optional override).
* Sends plain-text notifications to **Telegram** and **Discord** (no emoji).
* Console summary output (optional) for local runs.
* Configurable via `.env`.

---

## Requirements

* Python 3.8+
* Discord Server OR Telegram

---

## How to Install

1. **Clone the repo**

```powershell
git clone https://github.com/dracula0x79/HackNews.git
cd HackNews
```

2. **Install dependencies**

```powershell
pip install -r requirements.txt
```

Then open `.env` with Notepad and fill the required values (see next section).

---

## `.env` Configuration

Open `.env` and fill your actual tokens and settings.

**Example `.env`:**

```
SERPAPI_API_KEY=
GITHUB_TOKEN=
TWITTER_BEARER_TOKEN=  # Optional
NITTER_INSTANCE=https://nitter.net
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=   # Optional
POLL_INTERVAL_MINUTES=180
FETCH_FULL_ARTICLE=true
HASHTAGS=CVE,0day,exploit,infosec,bugbountytips,BugBounty,databreach
USER_MIN_NEWS=10
USER_MAX_NEWS=18
ALLOW_DUPLICATES=false
SHOW_SUMMARY=true
```

* `TELEGRAM_BOT_TOKEN` — token from BotFather.
* `TELEGRAM_CHAT_ID` — numeric chat id (user or group).
* `DISCORD_WEBHOOK_URL` — webhook URL for a channel (optional).
* `USER_MIN_NEWS` / `USER_MAX_NEWS` — number of items per run (min 5, max 20).
* `HASHTAGS` — comma-separated hashtags to monitor.
* `ALLOW_DUPLICATES` — `false` by default; set `true` to force notifications even if seen before.
* `SHOW_SUMMARY` — `true` shows console summary; `false` is silent.
* `TWITTER_BEARER_TOKEN` — optional; improves Twitter results.

---

## How to Create a Telegram Bot and Get `CHAT_ID`

### Create Bot and Get Token

1. In Telegram, start a chat with `@BotFather`.
2. Send `/newbot` and follow instructions.
3. BotFather returns a token like `123456789:ABCdefG...`. Put it into `TELEGRAM_BOT_TOKEN` in `.env`.

### Get Chat ID

1. Start a chat with your bot (send "hi") or add it to a group and send a message.
2. On your machine, request updates:

```powershell
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
```

Replace `<YOUR_TOKEN>` with your bot token. Look for `chat.id` in the returned JSON and copy it to `TELEGRAM_CHAT_ID`.

<img width="2868" height="1622" alt="image" src="https://github.com/user-attachments/assets/d9853a53-4f53-4b1e-87ae-5bb0e2da3d21" />

---

## How to Create a Discord Webhook

1. In Discord, open Server → Channel → Edit Channel → Integrations → Webhooks → New Webhook.
2. Copy the webhook URL and paste it into `DISCORD_WEBHOOK_URL` in `.env`.

<img width="2472" height="1021" alt="image" src="https://github.com/user-attachments/assets/93811142-bc1a-4d99-be13-e8a665cd92e8" />

---

## GitHub Token (Optional)

Why: Increases rate limit and enables GitHub code search API.

1. Go to [GitHub Tokens](https://github.com/settings/tokens)
2. Generate new token → select permissions (`repo` or `public_repo`, `read:packages`, `search`)
3. Copy the token and put it in `GITHUB_TOKEN` in `.env`
4. Keep it private.

<img width="2874" height="1480" alt="image" src="https://github.com/user-attachments/assets/c0dc9ddd-4b07-46b4-962f-1a9b9aef3341" />

---

## Run Once (Verbose)

```powershell
python tracker.py
```

<img width="2362" height="1263" alt="image" src="https://github.com/user-attachments/assets/3ccdd75c-cecc-4414-ba2f-7c21e90a82c0" />

---

## Schedule with Windows Task Scheduler

You can schedule the tracker to run automatically every day at **10:00 AM**.

> ⚠️ **Important:** Replace `PATH_TO` with the full path where you cloned the repository, e.g., `D:\Tools\HackNews`.
> Make sure the paths inside `run_tracker.bat` and `run_tracker_silent.vbs` match the actual folder location.

### Option 1 — Silent (Recommended)

Runs via a VBS wrapper so no CMD window is visible:

```cmd
schtasks /create /sc daily /st 10:00 /tn "HackNews Daily Tracker" /tr "wscript.exe \"D:\Tools\HackNews\run_tracker_silent.vbs\"" /f
```

* Edit `run_tracker_silent.vbs` if necessary to match the actual path of `run_tracker.bat`.

### Option 2 — Direct Batch (Visible Console)

Runs the batch file directly:

```cmd
schtasks /create /sc daily /st 10:00 /tn "HackNews Daily Tracker" /tr "\"D:\Tools\HackNews\run_tracker.bat\"" /f
```

* Make sure the `.bat` file has the correct path to `tracker.py` inside it.

---

### Test & Manage Task

* Run immediately:

```cmd
schtasks /run /tn "HackNews Daily Tracker"
```

* Verify task:

```cmd
schtasks /query /tn "HackNews Daily Tracker" /fo LIST /v
```

* Delete task:

```cmd
schtasks /delete /tn "HackNews Daily Tracker" /f
```

---

## How It Works

### Sources

* **RSS Feeds**: Reads from configured RSS feeds (`RSS_FEEDS`).
* **Reddit & Twitter**: Searches hashtags from `.env`.

If RSS entry is missing a publication date, it tries to extract `article:published_time` or other metadata from the webpage.

### Processing

* **Deduplication & Grouping**: Groups similar items using normalized title or unique ID.
* **Classification**: Categorizes items into **technique, attack, apt, security\_tech, vulnerability**.
* **Scoring & Ranking**: Scores items by unique sources and high-importance keywords (`ransomware`, `exploit`, `0day`, `apt`, `CVE`). Sorted descending.

### Duplicate Prevention

Uses `data/seen.json` to avoid notifying same items unless `ALLOW_DUPLICATES=true`.

### Notifications

Sends plain-text notifications to Telegram and Discord. Optional console summary (`SHOW_SUMMARY=true`) is not sent to channels.

### Optional Features

* **GitHub Code Search**: Optional via `GITHUB_TOKEN`. Returns potential PoC code — use carefully for defensive OSINT.

---

**Example Discord Webhook Message:** <img width="2750" height="1553" alt="image" src="https://github.com/user-attachments/assets/03eeb35a-4dbc-47b4-b9b8-be3f5c6f3092" />

**Example Telegram Notification:** <img width="2880" height="1660" alt="image" src="https://github.com/user-attachments/assets/42c5df2c-9df8-4b46-91af-bc692dc461db" />

---

