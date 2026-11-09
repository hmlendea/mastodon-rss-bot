# Integration Models

## Overview

This document describes the integration patterns with external systems: RSS feeds, linked web pages, Mastodon API, SQLite cache, privacy frontends, link monetisation, and media source rewriting.

## Integration Inventory

| Integration | Direction | Protocol | Authentication | Failure Impact |
|-------------|-----------|----------|----------------|----------------|
| RSS Feed | Inbound (fetch) | HTTP GET | None/feed-specific | Process exit |
| Linked Pages | Outbound (fetch) | HTTP GET | None | Entry continues without enrichment |
| Mastodon API | Outbound | HTTPS | OAuth Bearer | Entry skipped or process exit |
| SQLite Cache | Local | File I/O | None | Process exit |
| Privacy Frontends | Outbound (link rewrite) | None (string transform) | None | None |
| Link Shortening | Outbound | HTTP GET | None | Original link used |
| Link Monetisation | Outbound (link wrap) | None (string transform) | API key (hard-coded) | None |
| Media Sources | Outbound (fetch) | HTTP GET | None | Media skipped |
| Media Upload | Outbound | HTTPS | OAuth Bearer | Media skipped |

## RSS Feed Integration

### Pattern

**Pull-based batch fetch** — Application fetches feed on each scheduled run.

### Protocol

- **Method**: HTTP GET
- **URL**: Provided via `--rss` CLI argument
- **Format**: RSS 2.0, Atom 1.0 (auto-detected by feedparser)
- **Authentication**: None (public feeds) or feed-specific (operator responsibility)
- **Timeout**: None configured (feedparser/urllib defaults)
- **Headers**: Default feedparser headers

### Implementation

```python
feed = feedparser.parse(rss_feed_url)
```

### Data Extracted

| Field | Source | Used For |
|-------|--------|----------|
| `title` | `entry.title` | Identity hash, status text |
| `link` | `entry.link` | Identity hash, page fetch, status text |
| `published` | `entry.published` | Identity hash, age filter, cache |
| `summary` | `entry.summary` | Status text (optional) |
| `author` | `entry.author` | Status text (optional), cache |
| `tags` | `entry.tags` | Tag construction |
| `enclosures` | `entry.enclosures` | Media collection |

### Failure Modes

| Failure | Handling |
|---------|----------|
| Network error | Exception propagates, process exit 1 |
| Malformed feed | feedparser returns empty, 0 entries logged |
| Empty feed | 0 entries logged, process exits 0 |

### Limitations

- No ETag/If-Modified-Since support
- No incremental fetch (always full feed)
- No feed authentication mechanism
- No retry logic
- No timeout configuration

## Linked Page Integration

### Pattern

**Per-entry enrichment fetch** — Application fetches the linked page for each qualifying entry.

### Protocol

- **Method**: HTTP GET
- **URL**: `feed_entry.link`
- **Headers**: Rotating User-Agent via `fake-useragent`
- **Timeout**: None configured (urllib defaults)
- **Response**: HTML content

### Implementation

```python
req = urllib.request.Request(feed_entry.link, headers={'User-Agent': ua.random})
response = urllib.request.urlopen(req)
html_content = response.read()
soup = BeautifulSoup(html_content, 'lxml')
```

### Data Extracted

| Field | Source | Priority |
|-------|--------|----------|
| Title | `<meta property="og:title">` | 1 (highest) |
| Title | `<title>` | 2 |
| Title | `feed_entry.title` | 3 (fallback) |
| Image | `<meta property="og:image">` | Media source |

### Failure Modes

| Failure | Handling |
|---------|----------|
| Network error | Logged, `html_content = None`, continue |
| HTTP error (4xx/5xx) | Exception, logged, continue |
| Timeout | None configured (urllib default) |
| Malformed HTML | BeautifulSoup tolerant, partial parse |

### Limitations

- No robots.txt respect
- No rate limiting per domain
- No redirect limit configuration
- No JavaScript rendering (static HTML only)

## Mastodon API Integration

### Pattern

**Authenticated API client** — Application registers as a Mastodon app and posts statuses.

### Client Library

`Mastodon.py` — Python client for Mastodon API

### Authentication Flow

#### App Registration (One-time)

```python
Mastodon.create_app(
    rss_feed_domain,
    api_base_url='https://' + mastodon_instance,
    to_file="app_" + mastodon_instance + '.secret'
)
```

**Trigger**: `app_<instance>.secret` file missing
**Output**: App credentials file (client_id, client_secret)

#### User Authentication

```python
mastodon_api = Mastodon(
    access_token=mastodon_access_token,
    api_base_url='https://' + mastodon_instance
)
```

**Input**: `--access-token` CLI argument (OAuth bearer token)

### API Endpoints Used

| Endpoint | Method | Purpose | Failure Handling |
|----------|--------|---------|------------------|
| `media_post` | POST | Upload media | Log, skip media, continue |
| `status_post` | POST | Post status | Log, skip entry, continue |

### Media Upload

```python
media_response = mastodon_api.media_post(
    media_content,
    mime_type=detected_mime_type
)
media_ids.append(media_response['id'])
```

**Constraints**:
- Max 4 media per status (Mastodon limit)
- No pre-upload size check
- No video duration check

### Status Post

```python
mastodon_api.status_post(
    status=status_text,
    media_ids=media_ids
)
```

**Constraints**:
- 500 character limit (enforced by truncation)
- Media IDs from prior uploads

### Failure Modes

| Failure | Handling |
|---------|----------|
| App creation fails | Log, exit 1 |
| Authentication fails | Log, exit 1 |
| Media upload fails | Log, skip media, continue |
| Status post fails | Log, skip entry (no cache), continue |
| Rate limit (429) | Exception, logged, entry skipped |

### Limitations

- No rate limit awareness
- No retry logic
- No backoff strategy
- No pagination (no reading of own statuses)
- No streaming (no real-time updates)

## SQLite Cache Integration

### Pattern

**Append-only local cache** — SQLite database stores posted entry hashes.

### Schema

```sql
CREATE TABLE IF NOT EXISTS entries (
    entry_hash TEXT PRIMARY KEY,
    entry_title TEXT,
    entry_link TEXT,
    entry_published TEXT,
    entry_author TEXT
)
```

### Operations

| Operation | Method | SQL |
|-----------|--------|-----|
| Initialise | `init_db()` | `CREATE TABLE IF NOT EXISTS` |
| Lookup | `get_last_entry_posted()` | `SELECT * WHERE entry_hash = ?` |
| Insert | `save_posted_entry()` | `INSERT INTO entries VALUES (?, ?, ?, ?, ?)` |

### Implementation

```python
import sqlite3
sql = sqlite3.connect("cache.db")
db = sql.cursor()
```

### Failure Modes

| Failure | Handling |
|---------|----------|
| Connection error | Exception propagates, exit 1 |
| Table creation error | Exception propagates, exit 1 |
| Insert error (duplicate) | `IntegrityError`, propagates, exit 1 |
| Query error | Exception propagates, exit 1 |

### Limitations

- No UPDATE, no DELETE
- No TTL, no eviction
- No migration mechanism
- No WAL mode
- No connection pooling
- No concurrent access support

## Privacy Frontend Integration

### Pattern

**String transformation** — Domain replacement in links (no HTTP requests).

### Implementation

Hard-coded in `main.py` when `USE_PRIVACY_FRONTENDS=true`:

```python
if USE_PRIVACY_FRONTENDS:
    link = link.replace('old.reddit.com', 'reddit.com')
    link = link.replace('reddit.com', 'libreddit.kavin.rocks')
    link = link.replace('twitter.com', 'nitter.net')
    link = link.replace('youtube.com', 'yewtu.be')
```

### Mapping

| Original Domain | Replacement Domain |
|-----------------|-------------------|
| `old.reddit.com` | `reddit.com` |
| `reddit.com` | `libreddit.kavin.rocks` |
| `twitter.com` | `nitter.net` |
| `youtube.com` | `yewtu.be` |

### Limitations

- **Not configurable** — Requires code change
- **Order-dependent** — `old.reddit.com` → `reddit.com` → `libreddit.kavin.rocks` (double replacement)
- **No validation** — Replacement domains may be down
- **No fallback** — If frontend unavailable, link broken
- **Hard-coded instances** — Specific instances chosen (libreddit.kavin.rocks, nitter.net, yewtu.be)

## Link Shortening Integration

### Pattern

**HTTP GET to shortening service** — is.gd API.

### Implementation

```python
shortened = requests.get(
    'https://is.gd/create.php?format=simple&url=' + url
).text
```

### Service

- **Provider**: is.gd (hard-coded)
- **API**: Simple GET, returns shortened URL as plain text
- **Authentication**: None
- **Rate limits**: is.gd policy applies

### Failure Modes

| Failure | Handling |
|---------|----------|
| Network error | Exception, logged, original link used |
| Service error | Error text returned as "shortened" URL |

## Link Monetisation Integration

### Pattern

**String transformation** — URL wrapping via ShrinkMe.io (no HTTP request).

### Implementation

```python
monetised = (
    'https://shrinkme.io/st?api='
    '81ad7e29077269bcae6dc1773d87abbabeaa9aa8'
    '&url=' + urllib.parse.quote(link)
)
```

### Service

- **Provider**: ShrinkMe.io (hard-coded)
- **API key**: `81ad7e29077269bcae6dc1773d87abbabeaa9aa8` (embedded in source)
- **Format**: `https://shrinkme.io/st?api=<key>&url=<encoded_link>`

### Limitations

- **API key in source** — Not configurable, exposed in repository
- **No validation** — No check if key is valid
- **No analytics** — No click tracking integration

## Media Source Rewriting (Twitter → Nitter)

### Pattern

**URL transformation + fetch** — Rewrite Twitter media URLs to Nitter equivalents.

### Implementation

```python
# Rewrite pbs.twimg.com → nitter.unixfox.eu/pic/
media_url = media_url.replace(
    'https://pbs.twimg.com/media/',
    'https://nitter.unixfox.eu/pic/media%2F'
)
```

### Hard-coded Values

- **Nitter instance**: `nitter.unixfox.eu`
- **Path pattern**: `/pic/media%2F`

### Limitations

- **Not configurable** — Requires code change
- **Instance-specific** — Single Nitter instance hard-coded
- **Fragile** — Nitter instances change/disappear
- **No fallback** — If Nitter down, media unavailable

## Integration Security

### Data Exposure

| Integration | Data Sent | Data Received |
|-------------|-----------|---------------|
| RSS feed | None (GET only) | Feed content |
| Linked pages | User-Agent header | HTML content |
| Mastodon API | Access token, status text, media | API responses |
| is.gd | Original URL | Shortened URL |
| ShrinkMe.io | API key (in URL), original URL | Redirect URL |

### Credential Storage

| Credential | Storage | Location |
|------------|---------|----------|
| Mastodon app credentials | File | `app_<instance>.secret` |
| Mastodon access token | CLI argument | Process memory only |
| ShrinkMe API key | Source code | `main.py` (hard-coded) |

### Risks

1. **Access token in CLI args** — Visible in `ps` output, shell history
2. **ShrinkMe key in source** — Exposed in repository
3. **No TLS verification config** — Uses library defaults
4. **No certificate pinning** — Standard TLS only

## Related Documentation

- [Application Services](./application-services.md) — Services using integrations
- [Dependencies](../dependencies.md) — Integration boundaries
- [Security](../security.md) — Security considerations
- [Detail Mutation Flow](../flows/detail-mutation.md) — Integration sequence