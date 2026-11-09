# Main Pipeline API Reference

## Overview

This document describes the programmatic interface of `main.py` — the pipeline orchestrator. All business logic resides in this module.

## Module Structure

```
main.py
├── Imports (external + internal)
├── parse_args() → Namespace
├── main() → None
│   ├── Configuration loading (via config.py import)
│   ├── Database initialisation (via database.py)
│   ├── Mastodon app creation (conditional)
│   ├── Mastodon authentication
│   ├── Feed retrieval and parsing
│   ├── Entry iteration loop
│   │   ├── Field extraction
│   │   ├── Identity hashing
│   │   ├── Deduplication check
│   │   ├── Age filtering
│   │   ├── Linked page fetch
│   │   ├── Title extraction (3-tier)
│   │   ├── Ad filtering
│   │   ├── Media collection
│   │   ├── Media upload
│   │   ├── Link processing
│   │   ├── Author/tags construction
│   │   ├── Language detection
│   │   ├── Text replacements
│   │   ├── Status assembly
│   │   ├── Character truncation
│   │   ├── Status posting
│   │   └── Cache persistence
│   └── Exit
└── Module-level constants (from config.py)
```

## Functions

### `parse_args()`

**Signature**: `def parse_args() -> argparse.Namespace`

**Purpose**: Parse command-line arguments.

**Parameters**: None (reads `sys.argv`)

**Returns**: `argparse.Namespace` with attributes:
- `rss` (str) — RSS feed URL
- `instance` (str) — Mastodon instance domain
- `username` (str) — Mastodon username
- `access_token` (str) — OAuth access token
- `tags_to_add` (str | None) — Comma-separated tags
- `days_to_check` (int | None) — Age window in days

**Raises**: `SystemExit` (via argparse) on missing required args or invalid values

**Example**:
```python
args = parse_args()
rss_url = args.rss
instance = args.instance
```

### `main()`

**Signature**: `def main() -> None`

**Purpose**: Execute the full pipeline.

**Parameters**: None

**Returns**: None (exits via `sys.exit()` on error)

**Side Effects**:
- Reads `config.json` (via `config.py` import)
- Creates/reads `cache.db`
- Creates `app_<instance>.secret` (if missing)
- HTTP requests to RSS feed, linked pages, media URLs, link shortener
- Mastodon API calls (media upload, status post)
- stdout/stderr output

**Raises**: Propagates exceptions from config, database, feedparser, Mastodon

**Example**:
```python
if __name__ == '__main__':
    main()
```

## Module-Level Constants

Imported from `config.py` at module load:

| Constant | Type | Default | Source |
|----------|------|---------|--------|
| `INCLUDE_AUTHOR` | bool | `true` | `config.json` |
| `INCLUDE_LINK` | bool | `true` | `config.json` |
| `INCLUDE_LINK_THUMBNAIL` | bool | `true` | `config.json` |
| `USE_PRIVACY_FRONTENDS` | bool | `true` | `config.json` |
| `USE_SHORTLINK` | bool | `true` | `config.json` |
| `MONETISE_LINKS` | bool | `true` | `config.json` |
| `MAXIMUM_TOOTS_COUNT` | int | `10` | `config.json` |

**Note**: These are loaded at import time — changing `config.json` requires process restart.

## Internal Algorithms

### Identity Hashing

**Location**: `main()` entry loop

**Algorithm**:
```python
entry_hash = hashlib.md5(
    (feed_entry.title + feed_entry.link + feed_entry.published).encode()
).hexdigest()
```

**Input**: Entry title, link, published (concatenated, no separator)
**Output**: 32-char hex MD5 digest

### Date Parsing

**Location**: `main()` entry loop

**Formats** (tried in order):
1. `%a, %d %b %Y %H:%M:%S %z`
2. `%a, %d %b %Y %H:%M:%S %Z`
3. `%Y-%m-%dT%H:%M:%S%z`
4. `%Y-%m-%dT%H:%M:%S`

**Failure**: All formats fail → entry skipped

### Title Extraction

**Location**: `main()` entry loop

**Priority**:
1. `<meta property="og:title" content="...">`
2. `<title>` tag
3. `feed_entry.title` (fallback)

### Ad Filter

**Location**: `main()` entry loop

**Algorithm**:
```python
if 'ad' in title.lower():
    continue  # Skip entry
```

### Media Collection

**Location**: `main()` entry loop

**Sources** (priority order):
1. Twitter/X media (via Nitter rewrite)
2. Reddit media (via `.json` API)
3. OpenGraph images (`og:image`)
4. RSS enclosures

### Link Processing Pipeline

**Location**: `main()` entry loop

**Stages**:
1. Shortlink (is.gd) — if `USE_SHORTLINK`
2. Privacy frontends (domain replacement) — if `USE_PRIVACY_FRONTENDS`
3. Cleanup (tracking parameter removal)
4. Monetisation (ShrinkMe.io wrap) — if `MONETISE_LINKS`

### Status Assembly

**Location**: `main()` entry loop

**Components** (order):
1. Title
2. Author string (if `INCLUDE_AUTHOR`)
3. Link (if `INCLUDE_LINK`)
4. Tags
5. Summary (optional)

### Truncation

**Location**: `main()` entry loop

**Algorithm**:
```python
if len(status) > 500:
    status = status[:500]
```

## Data Structures

### Feed Entry (feedparser)

| Attribute | Type | Description |
|-----------|------|-------------|
| `title` | str | Entry title |
| `link` | str | Entry URL |
| `published` | str | Publication date string |
| `summary` | str | Entry summary (optional) |
| `author` | str | Entry author (optional) |
| `tags` | list | List of tag dicts with `term` key |
| `enclosures` | list | List of enclosure dicts with `href`/`url` |

### Cache Row (SQLite)

| Column | Type | Description |
|--------|------|-------------|
| `entry_hash` | TEXT | MD5 hash (primary key) |
| `entry_title` | TEXT | Entry title |
| `entry_link` | TEXT | Entry URL |
| `entry_published` | TEXT | Publication date string |
| `entry_author` | TEXT | Entry author |

### Mastodon Media Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Media ID for status_post |

## Error Handling

### Exception Propagation

| Stage | Exception | Handling |
|-------|-----------|----------|
| Config load | `FileNotFoundError`, `JSONDecodeError`, `KeyError` | Propagate, exit 1 |
| DB init | `sqlite3.Error` | Propagate, exit 1 |
| App creation | Any | Check return, exit 1 |
| Mastodon auth | Any | Catch, log, exit 1 |
| Feed parse | Any | Propagate, exit 1 |
| Page fetch | `urllib.error.URLError` | Log, continue |
| Media upload | `Mastodon.MastodonError` | Log, skip media |
| Status post | `Mastodon.MastodonError` | Log, skip entry |
| Cache insert | `sqlite3.Error` | Propagate, exit 1 |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Fatal error |

## Extension Hooks

### Dynamic Tags

**Loading**: `utils.try_import('dynamic_tags')`
**Call site**: Tag construction in entry loop
**Expected interface**: See [Extensions](./extensions.md)

### Text Replacements

**Loading**: `utils.try_import('text_replacements')`
**Call site**: Status assembly in entry loop
**Expected interface**: See [Extensions](./extensions.md)

## Usage Example

```python
# Programmatic invocation (not recommended — use CLI)
import sys
sys.argv = [
    'main.py',
    '--rss', 'https://example.com/feed.xml',
    '--instance', 'mastodon.social',
    '--username', 'user@example.com',
    '--access-token', 'abc123',
    '--tags-to-add', 'news,tech',
    '--days-to-check', '7'
]

from main import main
main()
```

## Related Documentation

- [API Reference Index](./INDEX.md) — All interfaces
- [Configuration Interface](../configuration.md) — Config module
- [Database Interface](../data-model.md) — Database module
- [Flows](../flows/) — Execution sequences
- [Components: Application Services](../components/application-services.md) — Algorithm details