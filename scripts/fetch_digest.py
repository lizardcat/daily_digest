import feedparser
import datetime
import os

# ── Configure your feeds here ──────────────────────────────────────────────
FEEDS = [
    {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "MIT Tech Review", "url": "https://www.technologyreview.com/feed/"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    {"name": "GitHub Blog", "url": "https://github.blog/feed/"},
    {"name": "Reuters Top News", "url": "https://feeds.reuters.com/reuters/topNews"},
    {"name": "Quanta Magazine", "url": "https://www.quantamagazine.org/feed/"},
]

ITEMS_PER_FEED = 5  # how many articles to grab per feed
DIGEST_DIR = "digests"  # folder where digest files are saved
# ───────────────────────────────────────────────────────────────────────────


def fetch_feed(feed_cfg: dict) -> list[dict]:
    """Parse a single RSS feed and return the top N items."""
    parsed = feedparser.parse(feed_cfg["url"])
    items = []
    for entry in parsed.entries[:ITEMS_PER_FEED]:
        items.append(
            {
                "title": entry.get("title", "No title").strip(),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "").strip()[:200],  # cap summary length
            }
        )
    return items


def build_markdown(date_str: str) -> str:
    lines = [f"# 📰 Daily RSS Digest — {date_str}\n"]

    for feed_cfg in FEEDS:
        lines.append(f"## {feed_cfg['name']}\n")
        try:
            items = fetch_feed(feed_cfg)
            if not items:
                lines.append("_No items found._\n")
            for item in items:
                lines.append(f"### [{item['title']}]({item['link']})")
                if item["summary"]:
                    # strip any html tags crudely
                    summary = item["summary"].replace("<p>", "").replace("</p>", "")
                    lines.append(f"> {summary}…\n")
                else:
                    lines.append("")
        except Exception as e:
            lines.append(f"_Error fetching feed: {e}_\n")

    lines.append("---")
    lines.append(f"_Generated automatically on {date_str}_")
    return "\n".join(lines)


def update_index(date_str: str, filename: str):
    """Keep a running index.md that links to every digest."""
    index_path = os.path.join(DIGEST_DIR, "index.md")
    entry = f"- [{date_str}]({filename})\n"

    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            content = f.read()
        # insert after the header line
        content = content.replace("---\n", f"---\n{entry}", 1)
    else:
        content = f"# Digest Archive\n\n---\n{entry}"

    with open(index_path, "w") as f:
        f.write(content)


def main():
    today = datetime.date.today()
    date_str = today.strftime("%Y-%m-%d")
    filename = f"{date_str}.md"
    out_path = os.path.join(DIGEST_DIR, filename)

    os.makedirs(DIGEST_DIR, exist_ok=True)

    print(f"Fetching digest for {date_str}…")
    markdown = build_markdown(date_str)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Saved → {out_path}")
    update_index(date_str, filename)
    print("Index updated.")


if __name__ == "__main__":
    main()
