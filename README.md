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
* Discord Server OR Telegram *
---

## How To Install

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


   
## `.env` configuration

Open `.env` file and fill your actual tokens and settings.

Example `.env`:

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
TWITTER_BEARER_TOKEN=
DISCORD_WEBHOOK_URL=
USER_MIN_NEWS=10
USER_MAX_NEWS=18
HASHTAGS=CVE,0day,exploit,infosec
ALLOW_DUPLICATES=false
SHOW_SUMMARY=true
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
   Browse "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
   Or
   curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates"
   ```
   Replace `<YOUR_TOKEN>` with the bot token. Look for `chat.id` in the returned JSON and copy that number to `TELEGRAM_CHAT_ID`.

<img width="2868" height="1622" alt="image" src="https://github.com/user-attachments/assets/d9853a53-4f53-4b1e-87ae-5bb0e2da3d21" />

---

## How to create a Discord webhook

1. In Discord, open Server → Channel → Edit Channel → Integrations → Webhooks → New Webhook.
2. Copy the webhook URL and paste it into `DISCORD_WEBHOOK_URL` in `.env`.

<img width="2472" height="1021" alt="image" src="https://github.com/user-attachments/assets/93811142-bc1a-4d99-be13-e8a665cd92e8" />

## GitHub token (if you want better code search)

Why: To increase the rate limit and get access to GitHub’s code search API.

How to get it:
1. Go to https://github.com/settings/tokens
2. Generate new token → Select permissions for repo or public_repo, read:packages, and search (if visible).
3. Copy the token and put it in GITHUB_TOKEN in .env .
4. Note: Keep the token personal and do not share it publicly.

<img width="2874" height="1480" alt="image" src="https://github.com/user-attachments/assets/c0dc9ddd-4b07-46b4-962f-1a9b9aef3341" />

---

4. **Run once (verbose)**

   ```powershell
   python tracker.py
   ```

   <img width="2362" height="1263" alt="image" src="https://github.com/user-attachments/assets/3ccdd75c-cecc-4414-ba2f-7c21e90a82c0" />

---

**But we will do it on Scheduler so that it will work automatically every day at 9:00 AM .**

5. **Schedule daily runs**
   Use `run_tracker.bat` with Windows Task Scheduler (steps below) to run at the time you choose.


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
     /c "C:\path\to\tracker-repo\run_tracker.bat"
     ```
   * Start in: `C:\path\to\tracker-repo`
5. Settings: enable "Run task as soon as possible if missed" if needed.
6. Save (you may be prompted for a Windows account password).

After the scheduled run you can check `tracker.log` (if using silent) or run a visible batch file to see the summary.

---

## How It Works :

**Sources**

Reads news from configured RSS feeds (RSS_FEEDS) plus Reddit & Twitter hashtag searches (HASHTAGS).

If an RSS entry lacks a publish date, the script fetches the article page and tries to extract article:published_time / <time datetime> metadata.

Only “today” items

The script keeps only items published on the same calendar day in X timezone (timezone). Older items are ignored.

Dedupe / grouping

Similar items are grouped by a normalized title key (fallback to SHA256(title||link)).

A group collects all links and sources where that story appeared.

**Classification**

Rule-based classification using keyword lists into:
technique, attack, apt, security_tech, vulnerability, or other.

Scoring / ranking

Score = number_of_distinct_sources + keyword_hits (keywords such as ransomware, exploit, 0day, apt, CVE, ...).

Items are sorted descending by score (then by number of sources).

Duplicate prevention

Each notified item gets an ID (SHA256(title||top_link)) stored in data/seen.json.

Items already in seen.json are not re-notified unless .env contains ALLOW_DUPLICATES=true (testing mode).

**Notifications**

Sends plain text notifications to Telegram and Discord.

Console summary output is optional (SHOW_SUMMARY=true), intended for local runs only — summaries are not sent to Telegram/Discord.

Optional: GitHub code search

You can optionally enable GitHub code search (requires GITHUB_TOKEN) to query repositories for relevant keywords. Use cautiously — results may include PoC code and must be used only for defensive OSINT.
 
 --- 
 
**Example Discord webhook message.**:
<img width="2750" height="1553" alt="image" src="https://github.com/user-attachments/assets/03eeb35a-4dbc-47b4-b9b8-be3f5c6f3092" />

**Example Telegram notification received.**:
<img width="2880" height="1660" alt="image" src="https://github.com/user-attachments/assets/42c5df2c-9df8-4b46-91af-bc692dc461db" />





