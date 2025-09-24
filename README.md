# HackNews

A simple Python tracker that collects **today’s** hacking / security news from popular RSS feeds, Reddit and Twitter hashtags, ranks and classifies them, and sends plain-text notifications to Telegram and Discord. Designed to be run automatically (for example via Task Scheduler) and safe for defensive OSINT use.

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
* Windows (instructions below); works on Linux too (use equivalent commands)

`requirements.txt`:

```
requests
feedparser
beautifulsoup4
lxml
python-dotenv
colorama
```

---

## Quick start

1. **Clone the repo**

   ```powershell
   git clone https://github.com/dracula0x79/HackNews.git
   cd HackNews
   ```

2. **Create and activate a virtual environment (recommended for Linux)**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install dependencies**

   ```powershell
   pip install -r requirements.txt
   ```

4. **Create `.env`**

   ```powershell
   copy .env.example .env
   ```

   Then open `.env` with Notepad and fill the required values (see next section).

5. **Run once (verbose)**

   ```powershell
   python tracker.py
   ```

   Or use `run_tracker.bat` to open a window and show the console summary.

6. **Schedule daily runs**
   Use `run_tracker_silent.bat` with Windows Task Scheduler (steps below) to run at the time you choose (e.g., 09:00).

---

## `.env` configuration

Copy `.env.example` to `.env` and fill your actual tokens and settings. **Do not commit `.env` to GitHub.**

Example `.env`:

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=

USER_MIN_NEWS=10
USER_MAX_NEWS=18
HASHTAGS=CVE,0day,exploit,infosec

ALLOW_DUPLICATES=false
SHOW_SUMMARY=true

TWITTER_BEARER_TOKEN=
```

* `TELEGRAM_BOT_TOKEN` — token from BotFather.
* `TELEGRAM_CHAT_ID` — numeric chat id (user or group).
* `DISCORD_WEBHOOK_URL` — webhook URL for a channel.
* `USER_MIN_NEWS` / `USER_MAX_NEWS` — how many items the script selects (min 5, max 20).
* `HASHTAGS` — comma-separated hashtags to monitor on Reddit/Twitter.
* `ALLOW_DUPLICATES` — `false` (default). Set `true` to force notifications even if seen before (for testing).
* `SHOW_SUMMARY` — `true` shows a console summary when the script runs; `false` is silent.
* `TWITTER_BEARER_TOKEN` (optional) — fill if you want better Twitter results.

---

## How to create a Telegram bot and get `CHAT_ID`

### Create bot and get token

1. In Telegram, start a chat with `@BotFather`.
2. Send `/newbot` and follow instructions to create a bot.
3. BotFather returns a token like `123456789:ABCdefG...`. Put it into `TELEGRAM_BOT_TOKEN` in `.env`.

### Get Chat ID

1. Start a chat with your new bot (send `hi`) or add it to a group and send a message.
2. On your machine, request updates:

   ```powershell
   curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
   ```

   Replace `<YOUR_TOKEN>` with the bot token. Look for `chat.id` in the returned JSON and copy that number to `TELEGRAM_CHAT_ID`.

   <img width="2868" height="1622" alt="image" src="https://github.com/user-attachments/assets/d9853a53-4f53-4b1e-87ae-5bb0e2da3d21" />

> Note: Group chat IDs may be negative or start with `-100...`. Use the value exactly as returned.

---

## How to create a Discord webhook

1. In Discord, open Server → Channel → Edit Channel → Integrations → Webhooks → New Webhook.
2. Copy the webhook URL and paste it into `DISCORD_WEBHOOK_URL` in `.env`.
<img width="2472" height="1021" alt="image" src="https://github.com/user-attachments/assets/93811142-bc1a-4d99-be13-e8a665cd92e8" />

## GitHub token (if you want better code search)

Why: To increase the rate limit and get access to GitHub’s code search API.

How to get it:
Go to https://github.com/settings/tokens

<img width="2874" height="1480" alt="image" src="https://github.com/user-attachments/assets/c0dc9ddd-4b07-46b4-962f-1a9b9aef3341" />


---

## Running:

* `run_tracker.bat`

---

## Schedule daily runs (Windows Task Scheduler example)

1. Open Task Scheduler → Create Task.
2. Name: `HackNews Daily Tracker`.
3. Triggers → New → Daily → Set time (e.g., 09:00) → OK.
4. Actions → New:

   * Program/script: `C:\Windows\System32\cmd.exe`
   * Add arguments:

     ```
     /c "C:\path\to\tracker-repo\run_tracker_silent.bat"
     ```
   * Start in: `C:\path\to\tracker-repo`
5. Settings: enable "Run task as soon as possible if missed" if needed.
6. Save (you may be prompted for a Windows account password).

After the scheduled run you can check `tracker.log` (if using silent) or run a visible batch file to see the summary.

---

## Troubleshooting

* **No Telegram messages**

  * Confirm `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`.
  * Test sending a message via API:

    ```powershell
    curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" -d chat_id=<CHAT_ID> -d text="test"
    ```
* **No Discord messages**

  * Open the webhook URL in a browser to test, or:

    ```powershell
    curl -H "Content-Type: application/json" -d "{\"content\":\"test\"}" <WEBHOOK_URL>
    ```
* **Script shows zero new items**

  * The script stores notifications in `data/seen.json`. Delete or edit that file to reset notifications for testing.
  * For testing-only, set `ALLOW_DUPLICATES=true` in `.env` to force notifications every run.
* **Twitter not returning data**

  * Fill `TWITTER_BEARER_TOKEN` if you want Twitter support. If empty, Twitter steps are skipped.

