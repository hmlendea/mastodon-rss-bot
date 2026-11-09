# Concurrency and Scheduling

## Overview

This document describes the concurrency model, scheduling mechanisms, and execution characteristics of the mastodon-rss-bot application.

## Concurrency Model

### Current Implementation

| Property | Value |
|----------|-------|
| **Processes** | Single process |
| **Threads** | Single thread (main thread only) |
| **Async/Await** | Not used |
| **Multiprocessing** | Not used |
| **Threading** | Not used |
| **Event Loop** | None |

### Execution Characteristics

```
Timeline of a Single Run:
┌─────────────────────────────────────────────────────────────────────┐
│                        PROCESS START                                 │
├─────────────────────────────────────────────────────────────────────┤
│  1. Config Load          │  ~10ms    │ Sequential, blocking         │
│  2. DB Init              │  ~5ms     │ Sequential, blocking         │
│  3. Mastodon Auth        │  ~100ms   │ Network I/O, blocking        │
│  4. Feed Fetch           │  ~500ms   │ Network I/O, blocking        │
│  5. Entry Loop (N entries)                                           │
│     ├── Page Fetch       │  ~200ms   │ Network I/O, blocking (each) │
│     ├── Media Download   │  ~500ms   │ Network I/O, blocking (each) │
│     ├── Media Upload     │  ~1000ms  │ Network I/O, blocking (each) │
│     ├── Link Shorten     │  ~300ms   │ Network I/O, blocking        │
│     └── Status Post      │  ~500ms   │ Network I/O, blocking        │
│  6. Cache Persist        │  ~5ms     │ Disk I/O, blocking           │
│  7. Process Exit         │  ~1ms     │                              │
└─────────────────────────────────────────────────────────────────────┘
```

### Implications

| Aspect | Impact |
|--------|--------|
| **Throughput** | Limited by sequential network I/O |
| **Latency** | Single entry = sum of all network calls |
| **Scalability** | Cannot process multiple entries in parallel |
| **Resource Usage** | Low CPU, moderate network, low memory |
| **Failure Isolation** | One entry failure doesn't affect others (except fatal errors) |

## Scheduling

### External Scheduler Required

The application **does not include a scheduler**. It is designed as a one-shot CLI tool that must be invoked periodically by an external scheduler.

### Supported Schedulers

| Scheduler | Configuration | Pros | Cons |
|-----------|---------------|------|------|
| **systemd timer** | `.timer` + `.service` files | Integrated, logging, dependencies | Linux only |
| **cron** | Crontab entry | Universal, simple | No dependency management |
| **Kubernetes CronJob** | YAML manifest | Cloud-native, scaling | Complex |
| **GitHub Actions** | Workflow schedule | Free, integrated | Limited runtime, no persistence |
| **Custom daemon** | Wrapper script | Full control | More code to maintain |

### Recommended: systemd Timer

**Service**: `mastodon-rss-bot.service` (Type=oneshot)
**Timer**: `mastodon-rss-bot.timer` (OnCalendar=*:0/15)

```ini
# /etc/systemd/system/mastodon-rss-bot.timer
[Timer]
OnCalendar=*:0/15          # Every 15 minutes
Persistent=true            # Run immediately if missed
RandomizedDelaySec=60      # Jitter to avoid thundering herd
```

### Scheduling Parameters

| Parameter | Recommended Value | Rationale |
|-----------|-------------------|-----------|
| **Interval** | 15-60 minutes | Balance freshness vs API rate limits |
| **Jitter** | 0-60 seconds | Avoid synchronized requests |
| **Timeout** | 10 minutes | Prevent stuck runs |
| **Retry** | On failure only | Don't retry success |

### Feed-Specific Scheduling

For multiple feeds with different freshness requirements:

```ini
# High-frequency feed (news)
mastodon-rss-bot-news.timer: OnCalendar=*:0/5

# Low-frequency feed (blog)
mastodon-rss-bot-blog.timer: OnCalendar=hourly
```

Each feed gets its own service/timer pair with separate working directory.

## Concurrency Control

### Current: None

No concurrency control mechanisms exist:
- No file locking on `cache.db`
- No process mutex
- No distributed lock

### Risks

| Scenario | Risk |
|----------|------|
| Timer fires while previous run active | Two processes writing to `cache.db` |
| Manual run during scheduled run | Database corruption, duplicate posts |
| Multiple feeds sharing directory | Cache collision |

### Mitigations (Current)

| Mitigation | Effectiveness |
|------------|---------------|
| `MAXIMUM_TOOTS_COUNT` limits run duration | Partial |
| Short run times (typically < 30s) | Partial |
| SQLite handles concurrent reads | Good for reads |

### Recommended: File Lock

```python
import fcntl

def acquire_lock(lock_path):
    lock_file = open(lock_path, 'w')
    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    return lock_file

def release_lock(lock_file):
    fcntl.flock(lock_file, fcntl.LOCK_UN)
    lock_file.close()
```

**Usage**: Acquire at startup, release at exit. Fail fast if lock held.

## Rate Limiting

### Mastodon API

**Limits** (instance-dependent, typical):
- 300 requests per 5 minutes (standard)
- 150 requests per 5 minutes (media upload)
- Per-account, per-IP

**Current Behavior**: No rate limit awareness — fires requests as fast as possible.

**Impact**: Large feeds may hit limits → 429 errors → failed posts.

### Recommended: Rate Limit Awareness

```python
import time

class RateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []

    def acquire(self):
        now = time.time()
        self.requests = [r for r in self.requests if r > now - self.window_seconds]
        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.window_seconds - now
            time.sleep(sleep_time)
        self.requests.append(time.time())
```

**Usage**: Wrap Mastodon API calls.

### Feed Fetch Rate Limiting

**Current**: No limit — fetches feed on every run.

**Recommendation**: Respect feed `ttl` or `sy:updateFrequency` if present.

```python
# feedparser provides feed.feed.ttl (minutes)
if hasattr(feed.feed, 'ttl'):
    min_interval = feed.feed.ttl * 60  # seconds
    # Skip if last fetch < min_interval ago
```

## Parallelism Opportunities

### Current: None

All operations sequential within a single run.

### Potential Parallelism

| Operation | Parallelizable? | Complexity | Benefit |
|-----------|-----------------|------------|---------|
| Multiple feeds | Yes (separate processes) | Low | Linear scale |
| Entry processing | Yes (thread pool) | Medium | 2-5x throughput |
| Media downloads | Yes (async/thread pool) | Medium | Overlap I/O |
| Media uploads | No (Mastodon serializes) | N/A | N/A |
| Page fetches | Yes (async/thread pool) | Medium | Overlap I/O |

### Recommended Architecture (Future)

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │ Feed 1  │        │ Feed 2  │        │ Feed N  │
   │ Process │        │ Process │        │ Process │
   └────┬────┘        └────┬────┘        └────┬────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                    ┌──────┴──────┐
                    │  Shared DB  │  (with locking)
                    └─────────────┘
```

Each feed process:
- Own working directory
- Own `cache.db` (or shared with locking)
- Own Mastodon app credentials
- Independent scheduling

## Resource Limits

### Current Limits

| Resource | Limit | Source |
|----------|-------|--------|
| Max entries per run | `MAXIMUM_TOOTS_COUNT` (default 10) | Config |
| Max media per toot | 4 | Mastodon API |
| Max status length | 500 chars | Mastodon API |
| Feed entries processed | All (reversed) | feedparser |
| Page fetch timeout | None (urllib default) | Library |
| Media download timeout | None (requests default) | Library |

### Recommended Limits

| Resource | Limit | Enforcement |
|----------|-------|-------------|
| Run duration | 10 minutes | systemd `TimeoutSec` |
| Page fetch timeout | 10 seconds | `urllib.request.urlopen(timeout=10)` |
| Media download timeout | 30 seconds | `requests.get(timeout=30)` |
| Mastodon API timeout | 30 seconds | Library config |
| Memory per run | 100 MB | Monitor, alert |
| Concurrent runs | 1 per feed | File lock |

## Monitoring Concurrency

### Metrics to Track

| Metric | Source | Alert |
|--------|--------|-------|
| Run duration | systemd/journal | > 5 minutes |
| Concurrent runs | Lock file | > 1 |
| Queue depth (future) | Custom | > 100 |
| Rate limit remaining | Mastodon headers | < 10 |

### Health Checks

```bash
# Check for stuck processes
ps aux | grep main.py

# Check lock file
ls -la /opt/mastodon-rss-bot/*.lock

# Check recent runs
journalctl -u mastodon-rss-bot.service --since "1 hour ago"
```

## Related Documentation

- [Build and Deployment](./build-and-deployment.md) — Scheduler configuration
- [Architecture](./architecture.md) — System context
- [Error Handling](./error-handling.md) — Timeout handling
- [Security](./security.md) — Rate limit security
- [Change Guide](./change-guide.md) — Adding concurrency