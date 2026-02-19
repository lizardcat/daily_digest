import feedparser
import datetime
import os

# ── Configure your feeds here ──────────────────────────────────────────────
FEEDS = [
    # Tech
    {"name": "Hacker News", "url": "https://news.ycombinator.com/rss"},
    {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
    {"name": "Ars Technica", "url": "https://feeds.arstechnica.com/arstechnica/index"},
    {"name": "Wired", "url": "https://www.wired.com/feed/rss"},
    # Science
    {"name": "Quanta Magazine", "url": "https://www.quantamagazine.org/feed/"},
    {"name": "NASA", "url": "https://www.nasa.gov/news-releases/feed/"},
    # News
    {"name": "Reuters", "url": "https://feeds.reuters.com/reuters/topNews"},
    {"name": "BBC News", "url": "https://feeds.bbci.co.uk/news/rss.xml"},
    {"name": "Associated Press", "url": "https://feeds.apnews.com/rss/apf-topnews"},
    # Business
    {"name": "Financial Times", "url": "https://www.ft.com/rss/home"},
    # Long reads
    {"name": "Quartz", "url": "https://qz.com/feed"},
    {"name": "Longreads", "url": "https://longreads.com/feed/"},
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


def strip_html(text: str) -> str:
    """Remove common HTML tags from summary text."""
    import re

    return re.sub(r"<[^>]+>", "", text).strip()


def build_markdown(date_str: str) -> str:
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    day = dt.strftime("%A, %B %d %Y")
    week_num = dt.strftime("%V")
    total_sources = len(FEEDS)

    # ── Header banner ────────────────────────────────────────────────────────
    lines = [
        f'<div align="center">',
        f"",
        f"# 📰 Daily Digest",
        f"### {day} &nbsp;•&nbsp; Week {week_num}",
        f"",
        f"![sources](https://img.shields.io/badge/sources-{total_sources}-blue?style=flat-square) "
        f"![articles](https://img.shields.io/badge/articles%20per%20feed-{ITEMS_PER_FEED}-green?style=flat-square) "
        f"![auto](https://img.shields.io/badge/auto--generated-✓-lightgrey?style=flat-square)",
        f"",
        f"</div>",
        f"",
        f"---",
        f"",
    ]

    # ── Table of contents ────────────────────────────────────────────────────
    lines.append("## 🗂 Contents")
    lines.append("")
    for feed_cfg in FEEDS:
        anchor = feed_cfg["name"].lower().replace(" ", "-").replace(".", "")
        lines.append(f"- [{feed_cfg['name']}](#{anchor})")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ── Feed sections ────────────────────────────────────────────────────────
    SECTION_EMOJIS = ["🔵", "🟢", "🟠", "🟣", "🔴", "🟡", "⚪"]

    for i, feed_cfg in enumerate(FEEDS):
        emoji = SECTION_EMOJIS[i % len(SECTION_EMOJIS)]
        lines.append(f"## {emoji} {feed_cfg['name']}")
        lines.append("")
        try:
            items = fetch_feed(feed_cfg)
            if not items:
                lines.append("> _No items found today._")
            for j, item in enumerate(items):
                # numbered title as a link
                lines.append(f"#### {j + 1}. [{item['title']}]({item['link']})")
                if item["summary"]:
                    summary = strip_html(item["summary"])[:280]
                    lines.append(f"> {summary}…")
                lines.append("")
                # divider between articles but not after the last one
                if j < len(items) - 1:
                    lines.append("<br>")
                    lines.append("")
        except Exception as e:
            lines.append(f"> ⚠️ _Error fetching feed: {e}_")

        lines.append("")
        lines.append("---")
        lines.append("")

    # ── Footer ───────────────────────────────────────────────────────────────
    lines += [
        '<div align="center">',
        "",
        f"_Generated automatically on {date_str}_",
        "",
        "⬆️ [Back to top](#-daily-digest)",
        "",
        "</div>",
    ]

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
