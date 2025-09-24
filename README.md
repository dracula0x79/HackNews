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

**We will schedule the script with Windows Task Scheduler so it runs automatically every day at 09:00.**

### Run automatically every day at 09:00 AM

```powershell
run_tracker.bat
```

**Schedule daily runs (Windows Task Scheduler)**

1. Open **Task Scheduler** and choose **Create Task...**.
2. **General**

   * Name: `HackNews Daily Tracker`
   * (Optional) Set "Run whether user is logged on or not" if you want it to run when you are signed out.
3. **Triggers** → **New\...**

   * Begin the task: **On a schedule** → **Daily**
   * Start: set the date and time (**09:00:00 AM**) → **OK**
4. **Actions** → **New\...**

   * Action: **Start a program**
   * **Program/script:** `C:\Windows\System32\cmd.exe`
   * **Add arguments:**

     ```
     /c "C:\path\to\tracker-repo\run_tracker.bat"
     ```

   * **Start in:**

     ```
     C:\path\to\tracker-repo
     ```
   * **OK**
5. **Save** the task. You may be prompted to enter the Windows account password to allow the task to run as that user.

---


### How It Works

---

### **Sources**
The script gathers news from multiple sources:
* **RSS Feeds**: It reads from a list of configured RSS feeds (`RSS_FEEDS`).
* **Reddit & Twitter**: It performs hashtag searches on Reddit and Twitter using the `HASHTAGS` list from the `.env` file.

If an RSS entry is missing a publication date, the script tries to extract the `article:published_time` or other date metadata directly from the article's webpage.

### **Processing**
The script only considers items published on the current calendar day, based on the `Africa/Cairo` timezone.

It then performs these steps:
* **Deduplication & Grouping**: Similar news items are grouped together using a normalized title or a unique ID generated from the title and link. This group collects all links and sources for that specific story.
* **Classification**: Each item is classified into categories like **technique**, **attack**, **apt**, **security_tech**, or **vulnerability** based on a list of keywords.
* **Scoring & Ranking**: A score is calculated for each item based on the number of unique sources and the presence of high-importance keywords such as `ransomware`, `exploit`, `0day`, `apt`, and `CVE`. The final list of items is sorted in descending order by score.

### **Duplicate Prevention**
To avoid sending the same notification multiple times, each item that is sent is given a unique ID and stored in `data/seen.json`. Items already in this file will not be notified again unless `ALLOW_DUPLICATES` is set to `true` in the `.env` file for testing purposes.

### **Notifications**
Once the items are processed and filtered, the script sends plain-text notifications to Telegram and Discord. A console summary can also be displayed during local runs by setting `SHOW_SUMMARY` to `true`. The summary is not sent to the notification channels.

### **Optional Features**
**GitHub Code Search:** You can enable an optional GitHub code search by providing a `GITHUB_TOKEN`. This feature queries repositories for relevant keywords and may return Proof of Concept (PoC) code, which should be used carefully for defensive OSINT purposes.
 --- 
 
**Example Discord webhook message.**:
<img width="2750" height="1553" alt="image" src="https://github.com/user-attachments/assets/03eeb35a-4dbc-47b4-b9b8-be3f5c6f3092" />

**Example Telegram notification received.**:
<img width="2880" height="1660" alt="image" src="https://github.com/user-attachments/assets/42c5df2c-9df8-4b46-91af-bc692dc461db" />





