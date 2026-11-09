# API Usage Examples

## Overview

This document provides practical code examples for using the mastodon-rss-bot application programmatically, extending it, and integrating it with other systems.

## Running the Application

### Basic Invocation

```bash
# Minimal run
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token "$MASTODON_ACCESS_TOKEN"
```

### Full Options

```bash
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token "$MASTODON_ACCESS_TOKEN" \
  --tags-to-add "news,tech,ai" \
  --days-to-check 7 \
  --maximum-toots-count 10
```

### With Environment Variables

```bash
# Export token to avoid ps exposure
export MASTODON_ACCESS_TOKEN="xxxx"

python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token "$MASTODON_ACCESS_TOKEN"
```

## Importing as Module

### Using Configuration Loader

```python
# Import configuration constants
import config

# Access loaded configuration
print(config.INCLUDE_AUTHOR)
print(config.INCLUDE_LINK)
print(config.USE_PRIVACY_FRONTENDS)
print(config.MAXIMUM_TOOTS_COUNT)

# Reload configuration (if config.json changed)
import importlib
importlib.reload(config)
```

### Using Database Functions

```python
import sqlite3
from database import init_db, get_last_entry_posted, save_posted_entry

# Initialize database
db = init_db()

# Check if entry was posted
last_posted = get_last_entry_posted(db, "entry-id-123", "https://example.com/post")
if last_posted:
    print(f"Already posted at {last_posted[0]}")
else:
    print("Not yet posted")

# Save posted entry
save_posted_entry(
    db,
    entry_id="entry-id-123",
    entry_link="https://example.com/post",
    entry_title="Example Title",
    entry_published="2024-01-15 10:30:00",
    status_url="https://mastodon.social/@user/123456"
)

db.close()
```

### Using Utility Functions

```python
from utils import detect_language, try_import

# Detect language
text = "Acesta este un text în limba română."
lang = detect_language(text)
print(lang)  # Output: "ro"

text_en = "This is an English text."
lang = detect_language(text_en)
print(lang)  # Output: "en"

# Try importing optional module
module = try_import("dynamic_tags")
if module:
    print("Extension available")
else:
    print("Extension not installed")
```

## Extension Examples

### Custom Dynamic Tags

```python
# dynamic_tags.py
from urllib.parse import urlparse

def get_dynamic_tags(entry, config):
    """Generate tags based on entry content."""
    tags = []

    # Domain-based tags
    domain = urlparse(entry.link).netloc
    domain_tags = {
        "github.com": "github",
        "arxiv.org": "research",
        "nytimes.com": "news",
        "bbc.com": "news",
    }
    if domain in domain_tags:
        tags.append(domain_tags[domain])

    # Content-based tags
    title_lower = entry.title.lower()
    if any(word in title_lower for word in ["security", "vulnerability", "cve"]):
        tags.append("security")
    if any(word in title_lower for word in ["release", "v1", "v2", "version"]):
        tags.append("release")

    # Config-driven tags
    if config.get("include_source_tag") and domain:
        tags.append(domain.split(".")[0])

    return tags
```

### Custom Text Replacements

```python
# text_replacements.py
import re

def apply_replacements(text, config):
    """Apply custom text transformations."""

    # Expand abbreviations
    abbreviations = {
        r"\bAI\b": "Artificial Intelligence",
        r"\bML\b": "Machine Learning",
        r"\bLLM\b": "Large Language Model",
    }
    for pattern, replacement in abbreviations.items():
        text = re.sub(pattern, replacement, text)

    # Remove tracking parameters (additional to built-in)
    text = re.sub(r'[?&](utm_[^&]+|fbclid|gclid)=[^&]*', '', text)
    text = re.sub(r'\?&', '?', text)
    text = re.sub(r'\?$', '', text)

    # Add attribution footer
    if config.get("add_footer"):
        text += "\n\n🤖 Automated by mastodon-rss-bot"

    return text
```

### Custom Media Filter

```python
# media_filters.py (proposed extension point)
def filter_media(media_urls, entry, config):
    """Filter which media URLs to process."""
    filtered = []
    for url in media_urls:
        # Skip small images
        if "thumb" in url or "small" in url:
            continue
        # Skip GIFs (if configured)
        if url.endswith(".gif") and not config.get("include_gifs"):
            continue
        filtered.append(url)
    return filtered
```

## Integration Examples

### Wrapping in Shell Script

```bash
#!/bin/bash
# run-bot.sh - Wrapper script with error handling

set -euo pipefail

BOT_DIR="/opt/mastodon-rss-bot"
LOG_FILE="/var/log/mastodon-rss-bot.log"

cd "$BOT_DIR"

# Run bot
if python main.py \
    --rss "${RSS_FEED_URL}" \
    --instance "${MASTODON_INSTANCE}" \
    --username "${MASTODON_USERNAME}" \
    --access-token "${MASTODON_ACCESS_TOKEN}" \
    --tags-to-add "${TAGS:-}" \
    --days-to-check "${DAYS:-7}" \
    >> "$LOG_FILE" 2>&1; then
    echo "$(date): Run completed successfully" >> "$LOG_FILE"
else
    echo "$(date): Run failed with exit code $?" >> "$LOG_FILE"
    # Optional: send alert
    # curl -X POST "$ALERT_WEBHOOK" -d "Bot run failed"
    exit 1
fi
```

### Monitoring with Health Check

```python
#!/usr/bin/env python3
"""health_check.py - Check if bot ran recently."""

import sqlite3
import sys
from datetime import datetime, timedelta

def check_last_run(db_path="cache.db", max_age_hours=2):
    """Check if any entry was posted within max_age_hours."""
    try:
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        cursor.execute("SELECT MAX(entry_published) FROM entries")
        result = cursor.fetchone()[0]
        db.close()

        if result is None:
            print("WARNING: No entries in cache")
            return False

        last_posted = datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
        age = datetime.now() - last_posted

        if age > timedelta(hours=max_age_hours):
            print(f"WARNING: Last post was {age} ago")
            return False

        print(f"OK: Last post {age} ago")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = check_last_run()
    sys.exit(0 if success else 1)
```

### Batch Processing Multiple Feeds

```python
#!/usr/bin/env python3
"""multi_feed.py - Process multiple feeds sequentially."""

import subprocess
import sys

FEEDS = [
    {"url": "https://blog.example.com/feed.xml", "tags": "blog,tech"},
    {"url": "https://news.example.com/rss", "tags": "news"},
    {"url": "https://youtube.com/feeds/videos.xml?channel_id=xxx", "tags": "video"},
]

INSTANCE = "mastodon.social"
USERNAME = "user@example.com"
TOKEN = "xxxx"  # Use env var in production

def run_feed(feed):
    cmd = [
        "python", "main.py",
        "--rss", feed["url"],
        "--instance", INSTANCE,
        "--username", USERNAME,
        "--access-token", TOKEN,
        "--tags-to-add", feed["tags"],
        "--days-to-check", "7",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"FAILED: {feed['url']}")
        print(result.stderr)
        return False
    else:
        print(f"OK: {feed['url']}")
        return True

def main():
    results = []
    for feed in FEEDS:
        success = run_feed(feed)
        results.append((feed["url"], success))

    print("\n=== Summary ===")
    for url, success in results:
        status = "✓" if success else "✗"
        print(f"{status} {url}")

    if not all(s for _, s in results):
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Testing with Mock Mastodon

```python
# test_integration.py
"""Integration test with mocked Mastodon API."""

from unittest.mock import Mock, patch
import main

def test_pipeline_with_mock():
    """Test full pipeline with mocked external services."""

    # Mock Mastodon client
    mock_mastodon = Mock()
    mock_mastodon.account_verify_credentials.return_value = Mock(id=12345)
    mock_mastodon.media_post.return_value = Mock(id="media_1")
    mock_mastodon.status_post.return_value = Mock(id="status_1", url="https://example.com/@user/1")

    # Mock feed fetch
    mock_feed = Mock()
    mock_feed.entries = [
        Mock(
            title="Test Entry",
            link="https://example.com/test",
            published="2024-01-15",
            summary="Test summary",
        )
    ]

    with patch("main.Mastodon", return_value=mock_mastodon), \
         patch("main.feedparser.parse", return_value=mock_feed), \
         patch("main.urllib.request.urlopen"), \
         patch("main.requests.get"):

        # Run pipeline
        main.main()

        # Assertions
        assert mock_mastodon.status_post.called
        assert mock_mastodon.media_post.called or True  # Optional
```

## Configuration Examples

### Minimal Configuration

```json
{
  "include_author": false,
  "include_link": true,
  "include_link_thumbnail": false,
  "use_privacy_frontends": false,
  "use_shortlink": false,
  "monetise_links": false,
  "maximum_toots_count": 5
}
```

### Privacy-Focused Configuration

```json
{
  "include_author": true,
  "include_link": true,
  "include_link_thumbnail": true,
  "use_privacy_frontends": true,
  "use_shortlink": false,
  "monetise_links": false,
  "maximum_toots_count": 10
}
```

### Maximum Engagement Configuration

```json
{
  "include_author": true,
  "include_link": true,
  "include_link_thumbnail": true,
  "use_privacy_frontends": false,
  "use_shortlink": true,
  "monetise_links": true,
  "maximum_toots_count": 20
}
```

## Troubleshooting Examples

### Debug Entry Processing

```python
# debug_entry.py - Inspect a single entry without posting
import feedparser
from utils import detect_language

feed = feedparser.parse("https://example.com/feed.xml")
entry = feed.entries[0]

print(f"Title: {entry.title}")
print(f"Link: {entry.link}")
print(f"Published: {entry.published}")
print(f"Summary: {entry.summary[:200]}...")
print(f"Language: {detect_language(entry.title)}")
print(f"Tags: {[t.term for t in entry.get('tags', [])]}")
```

### Test Title Extraction

```python
# test_title_extraction.py
from bs4 import BeautifulSoup
import urllib.request

url = "https://example.com/article"
html = urllib.request.urlopen(url).read().decode("utf-8")
soup = BeautifulSoup(html, "lxml")

# Tier 1: OpenGraph
og_title = soup.find("meta", property="og:title")
if og_title:
    print(f"OG Title: {og_title['content']}")

# Tier 2: First h1
h1 = soup.find("h1")
if h1:
    print(f"H1: {h1.get_text(strip=True)}")

# Tier 3: Title tag
title = soup.find("title")
if title:
    print(f"Title: {title.get_text(strip=True)}")
```

### Inspect Cache Database

```python
# inspect_cache.py
import sqlite3

db = sqlite3.connect("cache.db")
cursor = db.cursor()

# Count entries
cursor.execute("SELECT COUNT(*) FROM entries")
print(f"Total cached entries: {cursor.fetchone()[0]}")

# Recent entries
cursor.execute("""
    SELECT entry_id, entry_title, entry_published, status_url
    FROM entries
    ORDER BY rowid DESC
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"{row[2]} | {row[1][:50]} | {row[3]}")

db.close()
```

## Related Documentation

- [Quick Start](./quick-start.md) — First run guide
- [Configuration](./configuration.md) — Configuration options
- [API Reference Index](./api-reference/INDEX.md) — Module APIs
- [Troubleshooting](./troubleshooting.md) — Common issues
- [Integrations](./integrations.md) — External system integration