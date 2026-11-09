# Quick Start

## Overview

Get mastodon-rss-bot running in 5 minutes. This guide covers installation, configuration, first run, and scheduling.

## Prerequisites

| Requirement | Version | Check |
|-------------|---------|-------|
| Python | 3.x | `python --version` |
| pip | Any | `pip --version` |
| Network | Outbound HTTPS | `curl https://mastodon.social` |
| Mastodon account | Any instance | Have credentials ready |

## Step 1: Install

```bash
# Clone repository
git clone <repository-url>
cd mastodon-rss-bot

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Get Mastodon Access Token

1. Log in to your Mastodon instance
2. Go to **Settings → Development → New Application**
3. Fill in:
   - **Name**: `mastodon-rss-bot`
   - **Website**: (optional)
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob`
   - **Scopes**: `read`, `write`, `follow`
4. Click **Submit**
5. Copy the **Access token**

## Step 3: First Run

```bash
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username your_username@mastodon.social \
  --access-token "$MASTODON_ACCESS_TOKEN" \
  --days-to-check 1
```

**What happens**:
1. `config.json` created from `sample.config.json`
2. Mastodon app created, credentials saved to `app_mastodon.social.secret`
3. Feed fetched and parsed
4. New entries (within 1 day) posted to Mastodon
5. Cache updated in `cache.db`

**Expected output**:
```
Processing entry: Example Title
Posted: https://mastodon.social/@your_username/123456789
```

## Step 4: Verify

```bash
# Check Mastodon profile for new post
# Check cache database
sqlite3 cache.db "SELECT entry_title, status_url FROM entries;"

# Check files created
ls -la
# Should see: config.json, cache.db, app_mastodon.social.secret
```

## Step 5: Configure

Edit `config.json` to customize behavior:

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

See [Configuration](./configuration.md) for details.

## Step 6: Schedule

### Option A: systemd Timer (Recommended)

**Create service** `/etc/systemd/system/mastodon-rss-bot.service`:

```ini
[Unit]
Description=Mastodon RSS Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=your_user
WorkingDirectory=/path/to/mastodon-rss-bot
ExecStart=/path/to/mastodon-rss-bot/venv/bin/python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username your_username@mastodon.social \
  --access-token ${MASTODON_ACCESS_TOKEN} \
  --days-to-check 7
Environment=MASTODON_ACCESS_TOKEN=your_token_here

[Install]
WantedBy=multi-user.target
```

**Create timer** `/etc/systemd/system/mastodon-rss-bot.timer`:

```ini
[Unit]
Description=Run Mastodon RSS Bot every 15 minutes

[Timer]
OnCalendar=*:0/15
Persistent=true

[Install]
WantedBy=timers.target
```

**Enable**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mastodon-rss-bot.timer
sudo systemctl start mastodon-rss-bot.timer
sudo systemctl status mastodon-rss-bot.timer
```

### Option B: Cron

```bash
crontab -e
```

Add:

```cron
*/15 * * * * cd /path/to/mastodon-rss-bot && ./venv/bin/python main.py --rss https://example.com/feed.xml --instance mastodon.social --username your_username@mastodon.social --access-token "$MASTODON_ACCESS_TOKEN" --days-to-check 7 >> /var/log/mastodon-rss-bot.log 2>&1
```

## Step 7: Monitor

```bash
# Check timer status
systemctl status mastodon-rss-bot.timer

# Check recent runs
journalctl -u mastodon-rss-bot.service -n 50

# Check cache
sqlite3 cache.db "SELECT COUNT(*) FROM entries;"

# Check for errors
journalctl -u mastodon-rss-bot.service | grep -i error
```

## Common First-Run Issues

### "No new entries"

**Cause**: Feed has no entries within `--days-to-check`.

**Fix**: Increase days or check feed has recent content:

```bash
python -c "
import feedparser
feed = feedparser.parse('https://example.com/feed.xml')
print(f'Entries: {len(feed.entries)}')
for e in feed.entries[:3]:
    print(f'  {e.published} - {e.title}')
"
```

### "401 Unauthorized"

**Cause**: Invalid access token.

**Fix**: Regenerate token on Mastodon instance, update command.

### "ModuleNotFoundError"

**Cause**: Dependencies not installed.

**Fix**:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Database locked"

**Cause**: Another instance running.

**Fix**:
```bash
ps aux | grep main.py
# Kill stale process if needed
```

## Next Steps

- [Configuration](./configuration.md) — All options explained
- [Architecture](./architecture.md) — How it works
- [Build and Deployment](./build-and-deployment.md) — Production deployment
- [Troubleshooting](./troubleshooting.md) — Issue resolution
- [FAQ](./faq.md) — Common questions

## Command Reference

```bash
# Basic run
python main.py --rss <URL> --instance <INSTANCE> --username <USER> --access-token <TOKEN>

# With options
python main.py \
  --rss <URL> \
  --instance <INSTANCE> \
  --username <USER> \
  --access-token <TOKEN> \
  --tags-to-add "tag1,tag2" \
  --days-to-check 7 \
  --maximum-toots-count 10

# Help
python main.py --help
```

## Related Documentation

- [Configuration](./configuration.md) — Detailed configuration reference
- [Build and Deployment](./build-and-deployment.md) — Production deployment
- [Architecture](./architecture.md) — System design
- [Troubleshooting](./troubleshooting.md) — Issue resolution
- [FAQ](./faq.md) — Common questions