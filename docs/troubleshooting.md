# Troubleshooting

## Overview

This guide helps diagnose and resolve common issues with mastodon-rss-bot.

## Quick Diagnosis

### Check the Basics

```bash
# 1. Verify Python and dependencies
python --version
pip list | grep -E "feedparser|Mastodon|requests|beautifulsoup4|lxml|fake-useragent"

# 2. Check working directory
ls -la
# Should see: main.py, config.py, database.py, utils.py, config.json, cache.db, app_*.secret

# 3. Run with verbose output
python main.py --rss ... --instance ... --username ... --access-token ... 2>&1 | head -50
```

### Common Error Patterns

| Symptom | Likely Cause | Section |
|---------|--------------|---------|
| `ModuleNotFoundError` | Missing dependency | [Dependencies](#dependency-issues) |
| `sqlite3.OperationalError` | Database locked/corrupt | [Database Issues](#database-issues) |
| `MastodonAPIError` / `401` | Invalid token | [Authentication Issues](#authentication-issues) |
| `urllib.error.URLError` | Network/feed unreachable | [Network Issues](#network-issues) |
| `feedparser` returns empty | Feed format/URL issue | [Feed Issues](#feed-issues) |
| No output / exits silently | No new entries / age filter | [No Posts](#no-posts-issued) |
| Duplicate posts | Cache issue / feed change | [Duplicate Posts](#duplicate-posts) |

---

## Dependency Issues

### ModuleNotFoundError

```bash
# Error: ModuleNotFoundError: No module named 'feedparser'
# Fix: Install dependencies
pip install -r requirements.txt

# If using virtual environment, ensure it's activated
source venv/bin/activate
pip install -r requirements.txt
```

### Version Conflicts

```bash
# Check installed versions
pip list

# Reinstall clean
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Missing System Dependencies

```bash
# lxml may need system libraries
# Ubuntu/Debian:
sudo apt-get install libxml2-dev libxslt-dev python3-dev

# Fedora/RHEL:
sudo dnf install libxml2-devel libxslt-devel python3-devel

# Then reinstall
pip install --force-reinstall lxml
```

---

## Database Issues

### Database Locked

```bash
# Error: sqlite3.OperationalError: database is locked
# Cause: Another process holds the lock

# Check for running processes
ps aux | grep main.py

# Kill stale processes
pkill -f "python main.py"

# Remove lock file if exists
rm -f cache.db-wal cache.db-shm

# Retry
python main.py ...
```

### Database Corrupt

```bash
# Error: sqlite3.DatabaseError: database disk image is malformed
# Fix: Restore from backup or recreate

# Backup current (may be recoverable)
cp cache.db cache.db.corrupt.$(date +%s)

# Recreate (loses dedup history → duplicates possible)
rm cache.db
python main.py ...  # Recreates on first run
```

### Missing Database

```bash
# Error: sqlite3.OperationalError: no such table: entries
# Fix: Run init_db (happens automatically on first run)

# Or manually:
python -c "from database import init_db; init_db()"
```

### Cache Growth

```bash
# Check size
ls -lh cache.db
sqlite3 cache.db "SELECT COUNT(*) FROM entries;"

# If > 100MB or > 100k rows, consider cleanup
# (No built-in cleanup; see [Ambiguities](./ambiguities-and-open-questions.md#amb-009-cache-cleanup-policy))
```

---

## Authentication Issues

### Invalid Access Token

```bash
# Error: MastodonAPIError: 401 Unauthorized
# Or: MastodonAPIError: 403 Forbidden

# Causes:
# 1. Token expired/revoked
# 2. Token for wrong instance
# 3. Token lacks required scopes (read, write, follow)

# Fix:
# 1. Generate new token on Mastodon instance
# 2. Verify instance URL matches token
# 3. Ensure scopes include write
```

### App Credentials Issues

```bash
# Error: MastodonAPIError during app creation
# Or: File permission error on app_*.secret

# Fix:
# 1. Delete app secret file to force re-creation
rm app_mastodon.social.secret

# 2. Check file permissions
chmod 600 app_*.secret

# 3. Verify instance URL is correct (no trailing slash)
```

### Username Format

```bash
# Error: MastodonAPIError: 404 Not Found on verify_credentials

# Fix: Use full username with domain
# Correct: user@mastodon.social
# Incorrect: user
# Incorrect: @user@mastodon.social
```

---

## Network Issues

### Feed Unreachable

```bash
# Error: urllib.error.URLError: <urlopen error [Errno 111] Connection refused>
# Or: urllib.error.HTTPError: HTTP Error 404: Not Found

# Diagnose:
curl -I "https://example.com/feed.xml"
# Check: 200 OK, Content-Type: application/rss+xml or application/atom+xml

# Fix:
# 1. Verify feed URL is correct
# 2. Check network/firewall
# 3. Try alternative feed URL (e.g., /feed, /rss, /atom)
```

### Linked Page Unreachable

```bash
# Error: urllib.error.URLError during page fetch
# Symptom: Bot crashes on specific entry

# Diagnose:
curl -I "https://example.com/article"

# Fix:
# 1. Page may be temporarily down (retry on next run)
# 2. Page may block bots (check User-Agent)
# 3. Page may require JavaScript (not supported)
```

### Mastodon Instance Unreachable

```bash
# Error: requests.exceptions.ConnectionError
# Or: MastodonAPIError: connection timeout

# Diagnose:
curl -I "https://mastodon.social/api/v1/accounts/verify_credentials"

# Fix:
# 1. Check instance URL (no trailing slash)
# 2. Check network/firewall
# 3. Instance may be down or blocking
```

### Timeout Issues

```bash
# Symptom: Bot hangs indefinitely
# Cause: No timeout on urllib/requests calls

# Fix: Not currently configurable
# Workaround: Run with systemd timeout
# systemd: TimeoutSec=300 in service file
```

---

## Feed Issues

### Empty Feed

```bash
# Symptom: Bot runs, no posts, no errors
# Cause: Feed has no entries, or entries filtered out

# Diagnose:
python -c "
import feedparser
feed = feedparser.parse('https://example.com/feed.xml')
print(f'Entries: {len(feed.entries)}')
print(f'Feed title: {feed.feed.get(\"title\", \"N/A\")}')
for i, e in enumerate(feed.entries[:3]):
    print(f'  {i}: {e.title} - {e.link}')
"

# Fix:
# 1. Verify feed URL returns entries
# 2. Check --days-to-check not too small
# 3. Check entries not already in cache
```

### Malformed Feed

```bash
# Error: feedparser returns bozo=1
# Or: Entries missing expected fields

# Diagnose:
python -c "
import feedparser
feed = feedparser.parse('https://example.com/feed.xml')
print(f'Bozo: {feed.bozo}')
if feed.bozo:
    print(f'Bozo exception: {feed.bozo_exception}')
"

# Fix:
# 1. Feed may be invalid XML (contact feed provider)
# 2. Try alternative feed format (Atom vs RSS)
# 3. feedparser is lenient; usually works anyway
```

### Feed Encoding Issues

```bash
# Symptom: Garbled characters in titles
# Cause: Incorrect encoding detection

# Fix: feedparser handles most encodings
# If persistent, check feed declares encoding correctly
```

---

## No Posts Issued

### All Entries Already Cached

```bash
# Symptom: "0 new entries" or similar
# Cause: All entries already in cache.db

# Diagnose:
sqlite3 cache.db "SELECT entry_title, entry_published FROM entries ORDER BY rowid DESC LIMIT 5;"

# Fix:
# 1. Normal if no new content
# 2. To force re-post: delete cache.db (causes duplicates!)
# 3. Or wait for new feed entries
```

### Age Filter Too Restrictive

```bash
# Symptom: Entries exist but not posted
# Cause: --days-to-check excludes them

# Diagnose:
# Check entry published dates vs current date
python -c "
import feedparser
from datetime import datetime, timedelta
feed = feedparser.parse('https://example.com/feed.xml')
for e in feed.entries:
    pub = e.get('published', 'N/A')
    print(f'{pub} - {e.title[:50]}')
"

# Fix: Increase --days-to-check
python main.py ... --days-to-check 30
```

### Maximum Toots Reached

```bash
# Symptom: Only N entries posted per run
# Cause: MAXIMUM_TOOTS_COUNT limit (default 10)

# Fix: Increase limit
# config.json: "maximum_toots_count": 20
# Or CLI: --maximum-toots-count 20 (not implemented, use config)
```

---

## Duplicate Posts

### Cache Deleted or Corrupted

```bash
# Cause: cache.db removed or recreated
# Fix: Accept duplicates, or manually delete from Mastodon
```

### Feed Entry Changed

```bash
# Cause: Title, link, or published date changed in feed
# Result: Different MD5 hash → treated as new entry

# Diagnose:
# Compare current feed entry with cached entry
sqlite3 cache.db "SELECT entry_title, entry_link, entry_published FROM entries WHERE entry_link LIKE '%example%';"

# Fix: Not preventable with current hash scheme
# See [Ambiguities](./ambiguities-and-open-questions.md#amb-001-entry-identity-stability)
```

### Multiple Feeds, Same Content

```bash
# Cause: Same article in multiple feeds with different links
# Fix: Use canonical links, or accept duplicates
```

### Running from Different Directory

```bash
# Cause: Each working directory has its own cache.db
# Fix: Always run from same directory, or share cache.db
```

---

## Media Issues

### Media Not Attached

```bash
# Check stdout for media collection logs
# Look for: "Found X media items", "Uploaded media", "Failed to download"

# Common causes:
# 1. No media in entry (no images, no enclosures)
# 2. Media URL unreachable
# 3. Media type not supported (e.g., video too large)
# 4. Mastodon media upload failed
```

### Media Download Fails

```bash
# Error: requests.exceptions.RequestException
# Cause: Media URL blocked, requires auth, or too large

# Fix: Not currently handled gracefully
# Media is skipped, post proceeds without it
```

### Media Upload Fails

```bash
# Error: MastodonAPIError on media_post
# Cause: File too large, wrong format, rate limited

# Mastodon limits:
# - Image: 16 MB, 4096x4096
# - Video: 40 MB, 2:30 min
# - GIF: 8 MB

# Fix: Not currently handled
# Post may fail or proceed without media
```

---

## Link Processing Issues

### Shortlinks Not Working

```bash
# Check config.json: "use_shortlink": true
# Check ShrinkMe API reachable
curl "https://shrinkme.io/api?api=KEY&url=https://example.com"

# Note: API key is hard-coded in main.py
# If key invalid, shortlinks silently fail
```

### Privacy Frontends Not Applied

```bash
# Check config.json: "use_privacy_frontends": true
# Check link domain matches known frontends:
# - twitter.com / x.com → nitter.net
# - reddit.com → redlib
# - youtube.com → invidious
# - medium.com → scribe

# Frontends hard-coded in main.py
# If frontend down, behavior undefined
```

### Tracking Parameters Not Removed

```bash
# Built-in removal for: utm_*, fbclid, gclid
# Check if parameters use different names
# Add custom removal via text_replacements.py extension
```

---

## Performance Issues

### Run Takes Too Long

```bash
# Typical run: 10-30 seconds
# Slow run: > 60 seconds

# Diagnose:
# Add timing to identify bottleneck
# Common bottlenecks:
# 1. Feed fetch (slow server)
# 2. Page fetch (many linked pages)
# 3. Media download (large files)
# 4. Media upload (slow Mastodon)
# 5. Link shortening (ShrinkMe slow)

# Fix:
# 1. Reduce --days-to-check (fewer entries)
# 2. Reduce MAXIMUM_TOOTS_COUNT
# 3. Disable privacy frontends/shortlinks
# 4. Run during off-peak hours
```

### Memory Usage High

```bash
# Unlikely for this application
# Check for memory leaks in extensions
# Python process typically < 50 MB
```

---

## Scheduler Issues

### systemd Timer Not Running

```bash
# Check timer status
systemctl status mastodon-rss-bot.timer

# Check next run
systemctl list-timers | grep mastodon

# Check service logs
journalctl -u mastodon-rss-bot.service -n 50

# Common issues:
# 1. Timer not enabled: systemctl enable mastodon-rss-bot.timer
# 2. Timer not started: systemctl start mastodon-rss-bot.timer
# 3. Service fails: check journalctl for errors
# 4. WorkingDirectory wrong in service file
```

### Cron Not Running

```bash
# Check cron log
grep CRON /var/log/syslog | tail -20

# Check crontab
crontab -l

# Common issues:
# 1. PATH not set in cron (use full paths)
# 2. Virtual env not activated
# 3. Environment variables not set
# 4. Output not captured (check mail or log file)
```

---

## Debugging Techniques

### Enable Verbose Output

```bash
# The bot prints to stdout by default
# Run manually to see all output
python main.py --rss ... --instance ... --username ... --access-token ...
```

### Inspect Intermediate State

```python
# Add debug prints to main.py temporarily
# Or create debug script:

import feedparser
feed = feedparser.parse("https://example.com/feed.xml")
for e in feed.entries:
    print(f"Title: {e.title}")
    print(f"Link: {e.link}")
    print(f"Published: {e.published}")
    print(f"Summary: {e.summary[:100]}")
    print("---")
```

### Test Individual Components

```bash
# Test database
python -c "
from database import init_db, get_last_entry_posted, save_posted_entry
db = init_db()
print(get_last_entry_posted(db, 'test', 'https://example.com'))
db.close()
"

# Test config
python -c "import config; print(config.INCLUDE_AUTHOR, config.MAXIMUM_TOOTS_COUNT)"

# Test utils
python -c "from utils import detect_language; print(detect_language('Test text'))"
```

### Mock External Services

```python
# For testing without network
from unittest.mock import patch, Mock

with patch("main.feedparser.parse") as mock_parse, \
     patch("main.Mastodon") as mock_mastodon, \
     patch("main.urllib.request.urlopen") as mock_urlopen, \
     patch("main.requests.get") as mock_get:

    # Configure mocks
    mock_parse.return_value.entries = [...]
    mock_mastodon.return_value.status_post.return_value = Mock(id="123", url="...")

    # Run
    import main
    main.main()
```

---

## Getting Help

### Before Reporting

1. Check this troubleshooting guide
2. Check [FAQ](./faq.md)
3. Check [Ambiguities](./ambiguities-and-open-questions.md)
4. Run with full output and capture error
5. Note: Python version, OS, Mastodon instance

### Information to Include

- Full command line (redact token)
- Full error traceback
- Relevant log output
- `config.json` (redact nothing, no secrets)
- Python version: `python --version`
- Dependency versions: `pip list | grep -E "feedparser|Mastodon|requests|beautifulsoup4|lxml|fake-useragent"`

### Where to Report

- GitHub Issues (if repository has issues enabled)
- Check existing issues first
- Provide minimal reproduction case

---

## Related Documentation

- [FAQ](./faq.md) — Common questions
- [Error Handling](./error-handling.md) — Error behavior design
- [Ambiguities](./ambiguities-and-open-questions.md) — Known undefined behaviors
- [Build and Deployment](./build-and-deployment.md) — Scheduler setup
- [Architecture](./architecture.md) — System context