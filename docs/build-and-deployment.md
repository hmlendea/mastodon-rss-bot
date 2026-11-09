# Build and Deployment

## Overview

This document describes how to build, deploy, and operate the mastodon-rss-bot application in production environments.

## Build Process

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.x (unpinned) | Runtime |
| pip | Any | Package installation |
| SQLite | Any (stdlib) | Cache database |

### Build Steps

The application has **no build step** — it is interpreted Python with no compilation, bundling, or packaging.

```bash
# 1. Clone repository
git clone <repository-url>
cd mastodon-rss-bot

# 2. (Optional) Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python main.py --help
```

### Build Artifacts

**None** — No build artifacts produced. The source tree is the deployable unit.

### Packaging (Future)

For distribution, consider:

| Method | Tool | Output |
|--------|------|--------|
| Wheel | `setuptools` / `pyproject.toml` | `.whl` file |
| Standalone executable | `PyInstaller` / `Nuitka` | Single binary |
| Container image | `Docker` | OCI image |

## Deployment

### Deployment Topology

```
┌─────────────────────────────────────────────────────┐
│                   Host Machine                       │
│                                                      │
│  ┌────────────────────────────────────────────────┐ │
│  │              Systemd Service                    │ │
│  │  mastodon-rss-bot.service (oneshot)            │ │
│  │  └── python main.py --rss ... --instance ...   │ │
│  └────────────────────────────────────────────────┘ │
│                       │                              │
│  ┌────────────────────────────────────────────────┐ │
│  │              Systemd Timer                      │ │
│  │  mastodon-rss-bot.timer (OnCalendar=*)         │ │
│  └────────────────────────────────────────────────┘ │
│                       │                              │
│  ┌────────────────────────────────────────────────┐ │
│  │              Working Directory                  │ │
│  │  • main.py, config.py, database.py, utils.py   │ │
│  │  • config.json (runtime config)                │ │
│  │  • cache.db (SQLite)                           │ │
│  │  • app_<instance>.secret (Mastodon creds)      │ │
│  │  • logs/ (future)                              │ │
│  └────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │                    │                    │
         │ HTTPS              │ HTTPS              │ HTTPS
         ▼                    ▼                    ▼
   ┌───────────┐      ┌──────────────┐    ┌──────────────┐
   │ RSS Feed  │      │ Linked Pages │    │  Mastodon    │
   │  Server   │      │   (web)      │    │  Instance    │
   └───────────┘      └──────────────┘    └──────────────┘
```

### Deployment Requirements

| Requirement | Specification |
|-------------|---------------|
| OS | Linux (systemd recommended) |
| Python | 3.x |
| Network | Outbound HTTPS to feed, pages, Mastodon |
| Disk | Write access to working directory |
| Scheduler | systemd timer, cron, or external |
| Monitoring | Log aggregation (future) |

### Deployment Steps

#### 1. Prepare Environment

```bash
# Create deployment directory
sudo mkdir -p /opt/mastodon-rss-bot
sudo chown mastodon-bot:mastodon-bot /opt/mastodon-rss-bot

# Copy source files
cp main.py config.py database.py utils.py /opt/mastodon-rss-bot/
cp requirements.txt sample.config.json /opt/mastodon-rss-bot/

# Create virtual environment
cd /opt/mastodon-rss-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Create Configuration

```bash
# First run creates config.json from sample
python main.py --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token "$MASTODON_ACCESS_TOKEN"

# Edit config.json with desired values
nano config.json
```

#### 3. Create Mastodon App Credentials

The application auto-creates app credentials on first run:
- File: `app_<instance>.secret`
- Contains: client_id, client_secret
- Created by: `Mastodon.create_app()`

#### 4. Create Systemd Service

**File**: `/etc/systemd/system/mastodon-rss-bot.service`

```ini
[Unit]
Description=Mastodon RSS Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=mastodon-bot
Group=mastodon-bot
WorkingDirectory=/opt/mastodon-rss-bot
ExecStart=/opt/mastodon-rss-bot/venv/bin/python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token ${MASTODON_ACCESS_TOKEN} \
  --tags-to-add news,tech \
  --days-to-check 7
Environment=MASTODON_ACCESS_TOKEN=xxxx
# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/mastodon-rss-bot

[Install]
WantedBy=multi-user.target
```

#### 5. Create Systemd Timer

**File**: `/etc/systemd/system/mastodon-rss-bot.timer`

```ini
[Unit]
Description=Run Mastodon RSS Bot every 15 minutes

[Timer]
OnCalendar=*:0/15
Persistent=true
Unit=mastodon-rss-bot.service

[Install]
WantedBy=timers.target
```

#### 6. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable mastodon-rss-bot.timer
sudo systemctl start mastodon-rss-bot.timer

# Verify
sudo systemctl status mastodon-rss-bot.timer
sudo systemctl list-timers | grep mastodon
```

#### 7. Manual Run (Testing)

```bash
# Run once manually
sudo systemctl start mastodon-rss-bot.service

# Check logs
sudo journalctl -u mastodon-rss-bot.service -n 50
```

### Alternative: Cron

**Crontab** (`crontab -e`):

```cron
# Run every 15 minutes
*/15 * * * * cd /opt/mastodon-rss-bot && ./venv/bin/python main.py --rss https://example.com/feed.xml --instance mastodon.social --username user@example.com --access-token "$MASTODON_ACCESS_TOKEN" --tags-to-add news,tech --days-to-check 7 >> /var/log/mastodon-rss-bot.log 2>&1
```

### Alternative: Docker (Future)

**Dockerfile** (not yet created):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py config.py database.py utils.py sample.config.json ./

# Runtime configuration via environment variables
ENV RSS_FEED_URL=""
ENV MASTODON_INSTANCE=""
ENV MASTODON_USERNAME=""
ENV MASTODON_ACCESS_TOKEN=""

CMD ["python", "main.py", "--rss", "${RSS_FEED_URL}", "--instance", "${MASTODON_INSTANCE}", "--username", "${MASTODON_USERNAME}", "--access-token", "${MASTODON_ACCESS_TOKEN}"]
```

**docker-compose.yml** (not yet created):

```yaml
version: '3.8'
services:
  mastodon-rss-bot:
    build: .
    environment:
      - RSS_FEED_URL=${RSS_FEED_URL}
      - MASTODON_INSTANCE=${MASTODON_INSTANCE}
      - MASTODON_USERNAME=${MASTODON_USERNAME}
      - MASTODON_ACCESS_TOKEN=${MASTODON_ACCESS_TOKEN}
    volumes:
      - ./data:/app/data
    restart: "no"
```

## Configuration Management

### Configuration Files

| File | Purpose | Created By | Sensitive |
|------|---------|-----------|-----------|
| `config.json` | Runtime configuration | `load_config()` | No |
| `app_<instance>.secret` | Mastodon app credentials | `Mastodon.create_app()` | Yes |
| `cache.db` | Posted entry cache | `init_db()` | No |

### Environment Variables (Recommended)

| Variable | Purpose | Current Support |
|----------|---------|-----------------|
| `MASTODON_ACCESS_TOKEN` | Access token | Not supported (CLI arg only) |
| `RSS_FEED_URL` | Feed URL | Not supported (CLI arg only) |
| `MASTODON_INSTANCE` | Instance domain | Not supported (CLI arg only) |

**Recommendation**: Add environment variable support for sensitive values.

### Secrets Management

| Secret | Current Storage | Recommended Storage |
|--------|----------------|---------------------|
| Access token | CLI arg (visible in `ps`) | Environment variable or file |
| App credentials | File (`app_*.secret`) | File (acceptable) |
| ShrinkMe API key | Source code | Configuration or env var |

## Monitoring

### Current State

**No monitoring** — Only stdout/stderr output.

### Recommended Monitoring

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Pipeline success/failure | Exit code | Non-zero exit |
| Entries posted per run | Log count | 0 for N consecutive runs |
| Feed fetch duration | Timing log | > 60s |
| Mastodon API errors | Error log | Any 4xx/5xx |
| Cache size | `cache.db` file size | > 100 MB |
| Disk space | Filesystem | < 10% free |

### Health Check (Future)

```bash
# Check last successful run
systemctl status mastodon-rss-bot.service

# Check cache freshness
sqlite3 /opt/mastodon-rss-bot/cache.db "SELECT MAX(entry_published) FROM entries;"

# Check log for errors
journalctl -u mastodon-rss-bot.service --since "1 hour ago" | grep -i error
```

## Backup and Recovery

### Backup Strategy

| File | Backup Frequency | Method |
|------|------------------|--------|
| `cache.db` | Daily | `sqlite3 cache.db ".backup cache.db.bak"` |
| `app_*.secret` | On creation | Copy to secure storage |
| `config.json` | On change | Version control or copy |

### Recovery Procedure

1. Restore `cache.db` from backup
2. Restore `app_*.secret` from secure storage
3. Restore `config.json` from backup
4. Verify Mastodon token still valid
5. Run manual test: `python main.py --rss ... --instance ...`

### Cache Reset (Emergency)

```bash
# Stop service
sudo systemctl stop mastodon-rss-bot.timer

# Backup current cache
cp cache.db cache.db.backup.$(date +%Y%m%d)

# Remove cache (all entries will re-post if within age window)
rm cache.db

# Restart
sudo systemctl start mastodon-rss-bot.timer
```

**Warning**: Removing `cache.db` causes re-posting of all entries within the age window.

## Scaling Considerations

### Current Limitations

- Single process, single thread
- Sequential entry processing
- No parallelism
- No queue

### Scaling Options

| Approach | Complexity | Benefit |
|----------|-----------|---------|
| Multiple instances (different feeds) | Low | Parallel feeds |
| Queue-based architecture | High | Parallel entries, retry |
| Distributed workers | Very high | Horizontal scaling |

### Recommendation

For multiple feeds, run separate process per feed:

```bash
# Feed 1
python main.py --rss https://source1.com/feed.xml ...

# Feed 2
python main.py --rss https://source2.com/feed.xml ...
```

Each process maintains its own `cache.db` (use `--cache-path` in future).

## Rollback

### Application Rollback

```bash
# Git-based deployment
cd /opt/mastodon-rss-bot
git checkout <previous-tag>
source venv/bin/activate
pip install -r requirements.txt

# Restart timer
sudo systemctl restart mastodon-rss-bot.timer
```

### Configuration Rollback

```bash
# Restore previous config.json
cp config.json.backup config.json
```

## Related Documentation

- [Configuration](./configuration.md) — Configuration file details
- [Concurrency and Scheduling](./concurrency-and-scheduling.md) — Scheduler integration
- [Security](./security.md) — Deployment security hardening
- [Troubleshooting](./troubleshooting.md) — Deployment issue resolution
- [Quick Start](./quick-start.md) — First deployment guide