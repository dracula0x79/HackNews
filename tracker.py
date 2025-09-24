import os
import time
import json
import hashlib
import re
import threading
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import quote_plus, urlparse

import requests
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from colorama import init, Fore, Style

# --- init ---
init(autoreset=True)
load_dotenv()

# --- Config (from .env) ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

USER_MIN_NEWS = max(5, int(os.getenv("USER_MIN_NEWS") or 5))
USER_MAX_NEWS = min(20, int(os.getenv("USER_MAX_NEWS") or 10))

HASHTAGS = [h.strip() for h in (os.getenv("HASHTAGS") or "CVE,0day,exploit,infosec").split(",") if h.strip()]

ALLOW_DUPLICATES = os.getenv("ALLOW_DUPLICATES", "false").lower() in ("1","true","yes")
SHOW_SUMMARY = os.getenv("SHOW_SUMMARY", "true").lower() in ("1","true","yes")

# Paths
HERE = os.path.dirname(__file__)
DATA_DIR = os.path.join(HERE, "data")
os.makedirs(DATA_DIR, exist_ok=True)
SEEN_FILE = os.path.join(DATA_DIR, "seen.json")

# Timezone
CAIRO = ZoneInfo("Africa/Cairo")

# Popular hacking/security news RSS feeds (expanded)
RSS_FEEDS = [
    "https://thehackernews.com/feeds/posts/default?alt=rss",
    "https://blog.orange.tw/feed",
    "https://securityaffairs.co/wordpress/feed",
    "https://packetstormsecurity.com/feeds/atom.xml",
    "https://www.securityweek.com/feed/",
    "https://threatpost.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.zdnet.com/topic/security/rss.xml",
    "https://nakedsecurity.sophos.com/feed/",
]

# Keywords & classification rules
KEYWORDS_IMPORTANCE = [
    "attack", "campaign", "ransomware", "malware", "exploit", "0day", "zero-day",
    "poc", "cve", "breach", "data leak", "apt", "iot", "vulnerability", "rce"
]
CLASS_KEYWORDS = {
    "technique": ["technique", "tactic", "kill chain", "lateral movement", "mimikatz", "kerberoast", "tactics"],
    "attack": ["attack", "campaign", "breach", "incident", "compromise", "ransomware"],
    "apt": ["apt", "nation-state", "nation state", "threat actor", "group"],
    "security_tech": ["platform", "tool", "product", "release", "update", "vendor"],
    "vulnerability": ["vulnerability", "cve", "zero-day", "0day", "bug", "flaw"]
}

# ---------------- utilities ----------------
def load_seen():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, ensure_ascii=False, indent=2)

def now_cairo():
    return datetime.now(tz=CAIRO)

def norm_text(s):
    return re.sub(r"\s+", " ", (s or "").strip()).lower()

def make_id_from(title, link):
    return hashlib.sha256(( (title or "") + "||" + (link or "") ).encode("utf-8")).hexdigest()

def print_header():
    # Stylish header similar to pentest tools (no emoji)
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "VulnNews Tracker — Today's Hacking / Attack News".center(60))
    print(Fore.CYAN + ("Run at: " + now_cairo().strftime("%Y-%m-%d %H:%M:%S %Z")).center(60))
    print(Fore.CYAN + "=" * 60)

# ---------------- date helpers ----------------
def is_date_today(dt):
    if not dt:
        return False
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc).astimezone(CAIRO)
    else:
        dt = dt.astimezone(CAIRO)
    return dt.date() == now_cairo().date()

def parse_feed_date(entry):
    # handle feedparser published_parsed
    try:
        if entry.get("published_parsed"):
            return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        if entry.get("updated_parsed"):
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
    except Exception:
        pass
    # fallback: check entry fields
    for k in ("published","updated","updated_iso","pubDate"):
        if entry.get(k):
            try:
                s = entry.get(k)
                # try ISO parse
                s2 = s.replace("Z", "+00:00") if isinstance(s, str) else None
                if s2:
                    return datetime.fromisoformat(s2)
            except Exception:
                pass
    return None

# ---------------- fetchers ----------------
def fetch_feed(url):
    items = []
    try:
        feed = feedparser.parse(url)
        for e in feed.entries:
            title = e.get("title", "").strip()
            link = e.get("link", "").strip()
            snippet = e.get("summary", "") or e.get("description", "") or ""
            pub = parse_feed_date(e)
            items.append({"title": title, "link": link, "snippet": snippet, "published": pub, "source": url})
    except Exception:
        pass
    return items

def fetch_page_publish_date_and_snippet(url, timeout=10):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; VulnNewsTracker/1.0)"}
        r = requests.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        html = r.text
        soup = BeautifulSoup(html, "lxml")
        # gather date candidates
        dates = []
        for tag in soup.find_all(["meta", "time"]):
            if tag.name == "time" and tag.get("datetime"):
                dates.append(tag.get("datetime"))
            if tag.name == "meta":
                for attr in ("property", "name", "itemprop"):
                    v = tag.get(attr, "") or ""
                    if any(x in v.lower() for x in ["published","pubdate","date","dc.date","created"]):
                        if tag.get("content"):
                            dates.append(tag.get("content"))
                if tag.get("property") == "article:published_time" and tag.get("content"):
                    dates.append(tag.get("content"))
        parsed = None
        for cand in dates:
            try:
                s2 = cand.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(s2)
                break
            except Exception:
                continue
        # snippet: first paragraphs
        paragraphs = [p.get_text().strip() for p in soup.find_all("p") if p.get_text().strip()]
        snippet = "\n\n".join(paragraphs[:3])
        return {"published": parsed, "snippet": snippet}
    except Exception:
        return {"published": None, "snippet": ""}

# Reddit & Twitter lightweight
def reddit_search_rss(tag, limit=5):
    try:
        q = quote_plus(f"#{tag}")
        url = f"https://www.reddit.com/search.rss?q={q}&sort=new"
        return fetch_feed(url)[:limit]
    except Exception:
        return []

def twitter_search_recent(tag, limit=5):
    results = []
    token = os.getenv("TWITTER_BEARER_TOKEN")
    if not token:
        return results
    try:
        url = "https://api.twitter.com/2/tweets/search/recent"
        params = {"query": f"#{tag} -is:retweet", "max_results": str(min(limit,10)), "tweet.fields": "created_at,text"}
        r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=12)
        r.raise_for_status()
        for t in r.json().get("data", []):
            created = None
            if t.get("created_at"):
                try:
                    created = datetime.fromisoformat(t["created_at"].replace("Z","+00:00"))
                except Exception:
                    created = None
            results.append({"title": (t.get("text") or "")[:140], "link": f"https://twitter.com/i/web/status/{t.get('id')}", "snippet": t.get("text",""), "published": created, "source": "twitter"})
    except Exception:
        pass
    return results

# ---------------- classification & scoring ----------------
def classify(text, snippet=""):
    t = norm_text((text or "") + " " + (snippet or ""))
    for cat, keys in CLASS_KEYWORDS.items():
        for k in keys:
            if k in t:
                return cat
    if "apt" in t:
        return "apt"
    if "technique" in t or "tactic" in t:
        return "technique"
    if "cve" in t or "vulnerab" in t or "zero-day" in t or "0day" in t:
        return "vulnerability"
    return "other"

def score_item(title, snippet, sources_set):
    sc = len(sources_set)
    text = (title + " " + (snippet or "")).lower()
    for kw in KEYWORDS_IMPORTANCE:
        if kw in text:
            sc += 1
    return sc

# ---------------- notifiers ----------------
def notify_telegram_text(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode":"HTML", "disable_web_page_preview": True}
        r = requests.post(url, json=payload, timeout=12)
        return r.ok
    except Exception:
        return False

def notify_discord_text(text):
    if not DISCORD_WEBHOOK_URL:
        return False
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json={"content": text}, timeout=12)
        return r.ok
    except Exception:
        return False

# ---------------- main flow ----------------
def run_once(show_summary=True):
    seen = load_seen()
    candidates = []

    # RSS feeds
    for feed in RSS_FEEDS:
        items = fetch_feed(feed)
        for it in items:
            # if no published in feed, try fetching page
            if not it.get("published"):
                meta = fetch_page_publish_date_and_snippet(it.get("link"))
                it["published"] = meta.get("published")
                if not it.get("snippet"):
                    it["snippet"] = meta.get("snippet")
            candidates.append(it)
        time.sleep(0.4)

    # reddit & twitter from hashtags
    for tag in HASHTAGS:
        candidates.extend(reddit_search_rss(tag, limit=4))
        candidates.extend(twitter_search_recent(tag, limit=4))
        time.sleep(0.3)

    # filter to today's items (Cairo)
    today_items = [c for c in candidates if c.get("published") and is_date_today(c.get("published"))]

    # group by normalized title (simple dedupe)
    groups = {}
    for it in today_items:
        key = re.sub(r'[^a-z0-9]', '', norm_text(it.get("title","")))[:140] or make_id_from(it.get("title",""), it.get("link",""))
        g = groups.setdefault(key, {"title": it.get("title",""), "links": set(), "sources": set(), "snippets": [] , "published": it.get("published")})
        if it.get("link"):
            g["links"].add(it.get("link"))
        src = it.get("source") or urlparse(it.get("link") or "").netloc
        if src:
            g["sources"].add(src)
        if it.get("snippet"):
            g["snippets"].append(it.get("snippet"))

    items = []
    for g in groups.values():
        snippet = " ".join(g["snippets"][:2])
        cat = classify(g["title"], snippet)
        sc = score_item(g["title"], snippet, g["sources"])
        items.append({"title": g["title"], "links": list(g["links"]), "sources": list(g["sources"]), "snippet": snippet, "published": g["published"], "category": cat, "score": sc})

    # sort by score & number of sources (descending)
    items = sorted(items, key=lambda x: (x["score"], len(x["sources"])), reverse=True)

    # limit to user min/max
    count = max(USER_MIN_NEWS, min(USER_MAX_NEWS, len(items)))
    selected = items[:count]

    # prepare new_items according to ALLOW_DUPLICATES / seen
    new_items = []
    for it in selected:
        top_link = it["links"][0] if it.get("links") else ""
        rid = make_id_from(it.get("title",""), top_link)
        if ALLOW_DUPLICATES:
            # always notify
            new_items.append(it)
        else:
            if rid not in seen:
                seen[rid] = {"first_seen": now_cairo().isoformat(), "title": it.get("title")}
                new_items.append(it)

    # save seen if not allowing duplicates
    if not ALLOW_DUPLICATES:
        save_seen(seen)

    # send notifications
    for it in new_items:
        top_link = it["links"][0] if it.get("links") else ""
        text = f"{it['title']}\nCategory: {it['category']}\nScore: {it['score']}\nSources: {len(it['sources'])}\n{top_link}"
        notify_telegram_text(text)
        notify_discord_text(text)
        time.sleep(0.2)

    # console summary only (controlled by show_summary)
    if show_summary:
        print_header()
        print(Fore.YELLOW + f"Checked items today: {len(today_items)}")
        print(Fore.YELLOW + f"Selected (after ranking / limit): {len(selected)}")
        print(Fore.GREEN + f"New notifications sent: {len(new_items)}\n")
        if len(new_items) > 0:
            print(Fore.MAGENTA + "Top new items:")
            for idx, it in enumerate(new_items, 1):
                title = (it.get("title") or "")[:120]
                cat = it.get("category") or "other"
                sc = it.get("score") or 0
                sources = ", ".join(it.get("sources")[:4])
                print(Fore.WHITE + f"{idx}. {title}")
                print(Fore.WHITE + f"   Category: {cat} | Score: {sc} | Sources: {sources}")
                print(Fore.WHITE + f"   Link: {it['links'][0] if it.get('links') else 'N/A'}\n")
        else:
            print(Fore.BLUE + "No new items to notify.")
        print(Fore.CYAN + "=" * 60)

    return {"checked": len(today_items), "selected": len(selected), "notified": len(new_items)}

# ---------------- entrypoint ----------------
if __name__ == "__main__":
    # decide whether to show summary in console
    run_summary = SHOW_SUMMARY
    # Run once and exit (suitable for Task Scheduler)
    run_once(show_summary=run_summary)
