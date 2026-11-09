# System Invariants

## Overview

This document defines the invariants — properties that must always hold true — for the mastodon-rss-bot system. These invariants guide testing, validation, and regression detection.

## Data Invariants

### Cache Database

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Unique composite key** | `(entry_id, entry_link)` is unique | `UNIQUE` constraint in schema |
| **Non-null required fields** | `entry_id`, `entry_link`, `entry_title`, `entry_published` never NULL | `NOT NULL` constraints |
| **Status URL format** | `status_url` is valid Mastodon status URL or NULL | Regex: `^https://[^/]+/@[^/]+/\d+$` |
| **Published date format** | `entry_published` in `YYYY-MM-DD HH:MM:SS` format | Regex: `^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$` |
| **Monotonic growth** | Row count never decreases (no DELETE) | `SELECT COUNT(*)` non-decreasing |

### Entry Identity Hash

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Deterministic** | Same input → same MD5 hash | `hashlib.md5()` |
| **Fixed length** | Hash is 32 hex characters | `len(hash) == 32` |
| **Collision resistance** | Negligible collision probability for feed entries | N/A (property of MD5) |

### Configuration

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Config file exists** | `config.json` present after first run | `os.path.exists("config.json")` |
| **Valid JSON** | `config.json` parses without error | `json.load()` succeeds |
| **Known keys only** | No unknown keys in config (warning only) | Compare against schema |
| **Boolean values** | Toggle keys are boolean | `isinstance(v, bool)` |

## Behavioral Invariants

### Pipeline Execution

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Single run = single process** | No fork, no threads | `threading.active_count() == 1` |
| **Sequential entry processing** | Entries processed one at a time | No parallel execution |
| **Feed entries reversed** | Iteration order is `reversed(feed.entries)` | Code inspection |
| **Age filter applied** | Entries older than `--days-to-check` skipped | Check `entry_published` vs now |
| **Dedup check before processing** | Cache lookup before any enrichment | Code inspection |
| **Cache INSERT after successful post** | `save_posted_entry()` called after `status_post()` | Code inspection |

### Mastodon Posting

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Status length ≤ 500** | Final text truncated to 500 chars | `len(text) <= 500` |
| **Media count ≤ 4** | At most 4 media attachments | `len(media_ids) <= 4` |
| **Language field set** | `language` parameter from `detect_language()` | Code inspection |
| **Visibility default** | Default visibility (public) unless configured | Mastodon.py default |

### Media Handling

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Temp files deleted** | Local media files removed after upload | `os.path.exists()` check |
| **Media IDs from Mastodon** | `media_post()` returns valid ID | Type check |
| **No media = no media_ids** | Empty media list → empty media_ids | `len(media_ids) == 0` |

### Link Processing

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Shortlink only if enabled** | `USE_SHORTLINK` controls shortening | Config check |
| **Privacy frontend only if enabled** | `USE_PRIVACY_FRONTENDS` controls replacement | Config check |
| **Tracking params removed** | `utm_*`, `fbclid`, `gclid` stripped | Regex verification |
| **Monetisation only if enabled** | `MONETISE_LINKS` controls affiliate tags | Config check |

## State Invariants

### Runtime State

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Config loaded once** | Module-level constants set at import | Code inspection |
| **DB connection open during run** | `db` connection alive in `main()` | `db.total_changes >= 0` |
| **Mastodon client authenticated** | `verify_credentials()` succeeds | Exception if not |
| **Feed parsed before loop** | `feedparser.parse()` before entry iteration | Code inspection |

### File System

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **Working directory writable** | Can create `cache.db`, `config.json`, `app_*.secret` | `os.access(".", os.W_OK)` |
| **App secret per instance** | `app_<instance>.secret` naming | Filename pattern |
| **No orphan temp files** | Media files deleted after upload | `glob("*.tmp")` empty |

## Network Invariants

### Outbound Connections

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **HTTPS only** | All outbound connections use HTTPS | URL scheme check |
| **Feed URL from CLI** | `--rss` argument used for feed fetch | Code inspection |
| **Instance URL from CLI** | `--instance` argument used for Mastodon | Code inspection |
| **No inbound connections** | Application does not listen on any port | `netstat -tlnp` |

### Rate Limits

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **No rate limit awareness** | No backoff, no header checking | Code inspection |
| **Sequential API calls** | Mastodon calls serialized | Code inspection |

## Error Invariants

### Exception Handling

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **No try/except in main pipeline** | Exceptions propagate to top level | Code inspection |
| **Process exits non-zero on error** | Unhandled exception → exit code ≠ 0 | `sys.exit()` behavior |
| **No partial state on crash** | Cache not updated if post fails | Transaction atomicity |

### Logging

| Invariant | Description | Validation |
|-----------|-------------|------------|
| **All output to stdout** | `print()` used, no `logging` module | Code inspection |
| **No sensitive data in output** | Tokens, secrets not printed | Code inspection |
| **Progress visible** | Entry processing logged | `print()` calls in loop |

## Configuration Invariants

### Default Values

| Key | Default | Invariant |
|-----|---------|-----------|
| `include_author` | `false` | Boolean |
| `include_link` | `true` | Boolean |
| `include_link_thumbnail` | `false` | Boolean |
| `use_privacy_frontends` | `false` | Boolean |
| `use_shortlink` | `false` | Boolean |
| `monetise_links` | `true` | Boolean |
| `maximum_toots_count` | `10` | Integer > 0 |

### Sample Config Consistency

| Invariant | Description |
|-----------|-------------|
| **sample.config.json matches defaults** | All keys present with default values |
| **config.py reads all sample keys** | No key in sample missing from config.py |
| **No extra keys in config.py** | All config constants have sample entry |

## Extension Invariants

### Dynamic Tags

| Invariant | Description |
|-----------|-------------|
| **Returns list of strings** | `get_dynamic_tags()` → `list[str]` |
| **No side effects** | Pure function |
| **No exceptions** | Errors caught by caller |

### Text Replacements

| Invariant | Description |
|-----------|-------------|
| **Returns string** | `apply_replacements()` → `str` |
| **No side effects** | Pure function |
| **No exceptions** | Errors caught by caller |

## Validation Checklist

### Pre-Release Validation

Run these checks before any release:

```bash
# 1. Schema validation
sqlite3 cache.db ".schema entries"

# 2. Config validation
python -c "import config; print('Config OK')"

# 3. Import validation
python -c "import main, config, database, utils; print('Imports OK')"

# 4. Help text
python main.py --help

# 5. Dry run (if implemented)
# python main.py --dry-run ...

# 6. Link check
npx markdown-link-check docs/**/*.md
```

### Continuous Validation

| Check | Frequency | Method |
|-------|-----------|--------|
| Cache schema | On change | Code review |
| Config defaults | On change | Code review |
| Pipeline invariants | On change | Code review |
| Extension interfaces | On change | Code review |

## Invariant Violations

### Detection

| Violation | Detection Method |
|-----------|------------------|
| Duplicate cache entries | `UNIQUE` constraint violation |
| Null required fields | `NOT NULL` constraint violation |
| Status length > 500 | Runtime assertion |
| Media count > 4 | Runtime assertion |
| Temp files not deleted | File system scan |
| Sensitive data in logs | Log audit |

### Response

| Severity | Response |
|----------|----------|
| Data corruption | Immediate fix, cache rebuild |
| Security leak | Immediate fix, rotate secrets |
| Functional regression | Block release, add test |
| Performance regression | Investigate, optimize |

## Related Documentation

- [Data Model](./data-model.md) — Schema details
- [Error Handling](./error-handling.md) — Error behavior
- [State and Persistence](./state-and-persistence.md) — State management
- [Design Decisions](./design-decisions.md) — Architectural context
- [Testing](./testing.md) — Validation approach