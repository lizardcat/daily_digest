# 📰 Daily RSS Digest

Automatically fetches articles from RSS feeds every day, saves them as a Markdown file, and commits to this repo.

## How it works

1. GitHub Actions runs the workflow every day at 8 AM UTC
2. `scripts/fetch_digest.py` fetches the latest articles from your configured feeds
3. A Markdown digest is saved to `digests/YYYY-MM-DD.md`
4. The file is committed and pushed automatically

## Setup

### 1. Fork / clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/rss-digest.git
cd rss-digest
```

### 2. Customise your feeds

Open `scripts/fetch_digest.py` and edit the `FEEDS` list at the top:

```python
FEEDS = [
    {"name": "Hacker News",  "url": "https://news.ycombinator.com/rss"},
    {"name": "The Verge",    "url": "https://www.theverge.com/rss/index.xml"},
    # add as many as you like...
]
```

### 3. Adjust the schedule (optional)

In `.github/workflows/daily_digest.yml`, change the cron expression:

```yaml
- cron: "0 8 * * *" # 8:00 AM UTC daily
```

Use [crontab.guru](https://crontab.guru) to build your preferred schedule.

### 4. Push to GitHub

GitHub Actions will pick up the workflow automatically. You can also trigger it manually from the **Actions** tab → **Daily RSS Digest** → **Run workflow**.

## Running locally

```bash
pip install -r requirements.txt
python scripts/fetch_digest.py
```

## Project structure

```
.
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # GitHub Actions workflow
├── digests/
│   ├── index.md               # auto-generated archive index
│   └── YYYY-MM-DD.md          # one file per day
├── scripts/
│   └── fetch_digest.py        # main script
├── requirements.txt
└── README.md
```
