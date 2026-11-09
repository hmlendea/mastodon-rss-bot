# Integrations

## Overview

This document describes how mastodon-rss-bot integrates with external systems: RSS feeds, web pages, Mastodon, link shortening, privacy frontends, and media sources.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    mastodon-rss-bot                                  │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Feed     │  │ Page     │  │ Media    │  │ Link     │           │
│  │ Fetcher  │  │ Fetcher  │  │ Handler  │  │ Processor│           │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘           │
└───────┼─────────────┼─────────────┼─────────────┼──────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ RSS     │  │ Web      │  │ Media    │  │ Shortener│
   │ Feeds   │  │ Pages    │  │ Sources  │  │ Frontends│
   └─────────┘  └──────────┘  └──────────┘  └──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │   Mastodon   │
                   │   Instance   │
                   └──────────────┘
```

## RSS Feed Integration

### Protocol

| Property | Value |
|----------|-------|
| **Protocol** | HTTP/HTTPS GET |
| **Formats** | RSS 2.0, Atom 1.0, RDF (via feedparser) |
| **Authentication** | None (public feeds only) |
| **Encoding** | Auto-detected (UTF-8, ISO-8859-1, etc.) |
| **Library** | feedparser |

### Supported Feed Types

| Type | Detection | Notes |
|------|-----------|-------|
| RSS 2.0 | `<rss>` root element | Most common |
| Atom 1.0 | `<feed>` root element | Common for blogs |
| RDF/RSS 1.0 | `<rdf:RDF>` root element | Less common |
| JSON Feed | Not supported | feedparser limitation |

### Feed URL Requirements

| Requirement | Details |
|-------------|---------|
| **Scheme** | HTTP or HTTPS |
| **Content-Type** | `application/rss+xml`, `application/atom+xml`, `application/xml`, `text/xml` |
| **Accessibility** | Public (no auth) |
| **Rate limiting** | Respected if feed provides `ttl` |

### Feed Discovery

The bot does **not** discover feed URLs from web pages. The feed URL must be provided explicitly via `--rss`.

### Feed Parsing Behavior

```python
import feedparser

feed = feedparser.parse(feed_url)
# feed.entries: list of entry objects
# feed.feed: feed metadata (title, link, etc.)
# feed.bozo: 1 if parse error, 0 if clean
```

**Entry fields used**:
| Field | Used For | Required |
|-------|----------|----------|
| `entry.title` | Identity hash, post text | Yes |
| `entry.link` | Identity hash, post link | Yes |
| `entry.published` | Identity hash, age filter | Yes |
| `entry.summary` | Post text (if no page fetch) | No |
| `entry.tags` | Tags extraction | No |
| `entry.author` | Author attribution | No |
| `entry.enclosures` | Media (podcasts) | No |

### Integration Boundaries

| Boundary | Behavior |
|----------|----------|
| Feed unreachable | Exception propagates, run crashes |
| Feed malformed | feedparser returns bozo=1, may still parse |
| Feed empty | No entries, run exits normally |
| Feed slow | No timeout, may hang |

---

## Web Page Integration

### Protocol

| Property | Value |
|----------|-------|
| **Protocol** | HTTP/HTTPS GET |
| **Library** | urllib.request (stdlib) |
| **Parsing** | BeautifulSoup + lxml |
| **Authentication** | None |
| **JavaScript** | Not executed (static HTML only) |

### Page Fetch Behavior

```python
import urllib.request

request = urllib.request.Request(url, headers={"User-Agent": ua.random})
response = urllib.request.urlopen(request)
html = response.read().decode("utf-8", errors="ignore")
```

**User-Agent**: Rotating via `fake-useragent` library.

### Title Extraction

| Priority | Source | Selector |
|----------|--------|----------|
| 1 | OpenGraph | `<meta property="og:title">` |
| 2 | Heading | First `<h1>` |
| 3 | Title tag | `<title>` |

### Integration Boundaries

| Boundary | Behavior |
|----------|----------|
| Page unreachable | Exception propagates, run crashes |
| Page timeout | No timeout set, may hang |
| Page requires JS | Title extraction fails, falls back to feed title |
| Page blocks bots | 403 error, run crashes |
| Non-HTML content | Parsing may fail, falls back |

---

## Mastodon Integration

### Protocol

| Property | Value |
|----------|-------|
| **Protocol** | HTTPS (Mastodon REST API v1) |
| **Library** | Mastodon.py |
| **Authentication** | OAuth 2.0 Bearer token |
| **App creation** | Automatic via `Mastodon.create_app()` |

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/apps` | POST | Create app (get client credentials) |
| `/oauth/token` | POST | Exchange credentials for access token (if needed) |
| `/api/v1/accounts/verify_credentials` | GET | Verify token, get account info |
| `/api/v2/media` | POST | Upload media attachment |
| `/api/v1/statuses` | POST | Post status with media |

### Authentication Flow

```
1. Mastodon.create_app(
     "mastodon-rss-bot",
     api_base_url="https://<instance>",
     to_file="app_<instance>.secret"
   )
   → Creates app_<instance>.secret with client_id, client_secret

2. Mastodon(
     client_id=...,
     client_secret=...,
     access_token="<CLI arg>",
     api_base_url="https://<instance>"
   )
   → Authenticated client

3. mastodon.account_verify_credentials()
   → Verifies token, gets account
```

### Status Posting

```python
mastodon.status_post(
    status=entry_text,        # str, max 500 chars
    media_ids=media_ids,      # list of media IDs (max 4)
    language=detected_lang,   # str, e.g., "en", "ro", "und"
    # visibility not set → default (public)
)
```

### Media Upload

```python
media = mastodon.media_post(
    media_file=file_path,     # path to local file
    mime_type="image/jpeg",   # detected from extension
    description=None          # alt text not set
)
media_id = media["id"]
```

### Integration Boundaries

| Boundary | Behavior |
|----------|----------|
| Invalid token | 401 error, run crashes |
| Rate limited (429) | Exception, run crashes |
| Instance down | Connection error, run crashes |
| Media too large | Upload fails, run crashes |
| Status too long | Truncated to 500 chars before posting |
| Too many media | Undefined (see AMB-003) |

### Rate Limits

| Limit | Typical Value | Bot Awareness |
|-------|---------------|---------------|
| Status posts | 300 per 5 min | None |
| Media uploads | 150 per 5 min | None |
| API calls | 300 per 5 min | None |

**No rate limit headers checked. No backoff implemented.**

---

## Link Shortening Integration

### Service: ShrinkMe

| Property | Value |
|----------|-------|
| **Service** | ShrinkMe (shrinkme.io) |
| **API** | REST GET |
| **Authentication** | API key (hard-coded in source) |
| **Library** | requests |

### API Call

```python
import requests

response = requests.get(
    f"https://shrinkme.io/api?api={API_KEY}&url={original_url}"
)
short_url = response.text  # Plain text response
```

### Integration Boundaries

| Boundary | Behavior |
|----------|----------|
| Service down | Exception, run crashes (if enabled) |
| Invalid API key | Error response, shortlink fails |
| Rate limited | Undefined behavior |
| Disabled in config | Not called |

### Security Concern

The API key is hard-coded in `main.py`. If the repository is public, the key is exposed. See [Security](./security.md).

---

## Privacy Frontend Integration

### Purpose

Replace tracking-heavy URLs with privacy-respecting frontend alternatives.

### Supported Frontends

| Service | Original Domain | Frontend | Notes |
|---------|----------------|----------|-------|
| Twitter/X | `twitter.com`, `x.com` | `nitter.net` | Hard-coded endpoint |
| Reddit | `reddit.com` | Redlib instance | Hard-coded |
| YouTube | `youtube.com` | Invidious instance | Hard-coded |
| Medium | `medium.com` | Scribe | Hard-coded |

### Transformation Logic

```python
# Pseudocode
if USE_PRIVACY_FRONTENDS:
    if "twitter.com" in url or "x.com" in url:
        url = url.replace("twitter.com", "nitter.net")
        url = url.replace("x.com", "nitter.net")
    elif "reddit.com" in url:
        url = url.replace("reddit.com", "<redlib-instance>")
    # ... etc
```

### Integration Boundaries

| Boundary | Behavior |
|----------|----------|
| Frontend down | Link broken (no fallback) |
| Frontend blocked | Link broken (no fallback) |
| Unknown domain | No transformation |
| Disabled in config | No transformation |

### Limitations

- Single frontend per service (no fallback chain)
- Hard-coded frontend URLs
- No availability checking
- No automatic frontend discovery

---

## Media Source Integrations

### Twitter/X → Nitter

| Property | Value |
|----------|-------|
| **Source** | Twitter/X URLs in feed content |
| **Transformation** | Replace domain with Nitter |
| **Media extraction** | Parse Nitter page for images/videos |
| **Library** | BeautifulSoup |

### Reddit

| Property | Value |
|----------|-------|
| **Source** | Reddit URLs in feed content |
| **Transformation** | Replace domain with Redlib |
| **Media extraction** | Parse Reddit JSON API or page |
| **Library** | requests, BeautifulSoup |

### OpenGraph

| Property | Value |
|----------|-------|
| **Source** | `<meta property="og:image">` in linked page |
| **Extraction** | BeautifulSoup meta tag parsing |
| **Library** | BeautifulSoup |

### RSS Enclosures

| Property | Value |
|----------|-------|
| **Source** | `<enclosure>` tags in feed entries |
| **Types** | Images, audio, video |
| **Extraction** | feedparser `entry.enclosures` |

### Media Download

```python
import requests

response = requests.get(media_url, headers={"User-Agent": ua.random})
with open(local_path, "wb") as f:
    f.write(response.content)
```

**Library**: requests
**User-Agent**: Rotating via fake-useragent
**Timeout**: None (default)

### Media Upload

See [Mastodon Integration](#mastodon-integration).

---

## Integration Summary

| System | Protocol | Library | Auth | Timeout | Error Handling |
|--------|----------|---------|------|---------|----------------|
| RSS Feed | HTTPS GET | feedparser | None | None | Crash |
| Web Page | HTTPS GET | urllib | None | None | Crash |
| Mastodon API | HTTPS REST | Mastodon.py | OAuth2 | Library default | Crash |
| ShrinkMe | HTTPS GET | requests | API key (hard-coded) | None | Crash |
| Privacy Frontends | N/A (URL rewrite) | None | None | N/A | N/A |
| Media Download | HTTPS GET | requests | None | None | Crash |
| Media Upload | HTTPS POST | Mastodon.py | OAuth2 | Library default | Crash |

## Integration Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Feed provider changes format | Parse failure | feedparser is lenient |
| Page structure changes | Title extraction fails | 3-tier fallback |
| Mastodon API changes | Posting fails | Monitor Mastodon.py updates |
| ShrinkMe outage | Shortlinks fail | Disable in config |
| Frontend outage | Broken links | Disable in config |
| Nitter/Redlib shutdown | Media extraction fails | Disable privacy frontends |
| Rate limiting | Posts fail | Reduce frequency |

## Related Documentation

- [Dependencies](./dependencies.md) — Library details
- [Architecture](./architecture.md) — System context
- [Integration Models](./components/integration-models.md) — Component view
- [Security](./security.md) — Security considerations
- [Troubleshooting](./troubleshooting.md) — Integration issue resolution