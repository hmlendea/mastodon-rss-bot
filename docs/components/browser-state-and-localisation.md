# Browser State and Localisation

## Overview

This document describes the HTTP client state management, User-Agent rotation, and language detection/localisation features in the application.

## HTTP Client State

### No Persistent Session

The application does **not** maintain a persistent HTTP session or cookie jar across requests. Each HTTP request is independent:

- **RSS feed fetch**: `feedparser.parse(url)` — uses feedparser's internal handling
- **Linked page fetch**: `urllib.request.urlopen()` — new connection per request
- **Media download**: `requests.get()` — new connection per request
- **Link shortening**: `requests.get()` — new connection per request
- **Mastodon API**: `Mastodon.py` library — manages its own connection pooling

### Implications

- No cookie persistence across requests
- No automatic redirect handling beyond library defaults
- No connection reuse (except Mastodon.py internal)
- Each request establishes new TLS connection

## User-Agent Rotation

### Implementation

```python
from fake_useragent import UserAgent
ua = UserAgent()
headers = {'User-Agent': ua.random}
```

### Behavior

- **Library**: `fake-useragent`
- **Source**: Fetches User-Agent list from upstream on first use
- **Caching**: Caches locally in `~/.fake_useragent.json` (or similar)
- **Rotation**: `ua.random` returns a random User-Agent string per call
- **Usage**: Applied to:
  - Linked page fetches (`urllib.request`)
  - Media downloads (`requests`)
  - Link shortening (`requests`)

### Failure Modes

- **First run**: Network request to fetch UA list (may fail offline)
- **Upstream changes**: UA list may become stale
- **Blocking**: Some sites block known fake UAs

### Configuration

**Not configurable** — No option to:
- Disable rotation
- Set custom User-Agent
- Use fixed User-Agent
- Configure UA source

## Language Detection

### Implementation (`utils.py:detect_language()`)

```python
def detect_language(text):
    # Check Romanian diacritics
    romanian_chars = set('ăâîșțĂÂÎȘȚ')
    if any(c in text for c in romanian_chars):
        return 'ro'

    # Keyword counting
    ro_keywords = {'și', 'în', 'pentru', 'cu', 'pe', 'la', 'de', 'din', 'a', 'este', 'sunt'}
    en_keywords = {'the', 'and', 'for', 'with', 'in', 'on', 'at', 'to', 'of', 'is', 'are'}

    text_lower = text.lower()
    ro_count = sum(1 for w in ro_keywords if w in text_lower)
    en_count = sum(1 for w in en_keywords if w in text_lower)

    return 'ro' if ro_count > en_count else 'en'
```

### Algorithm

1. **Diacritic check**: If any Romanian diacritic present → `'ro'`
2. **Keyword counting**: Count Romanian vs English stopwords
3. **Majority wins**: Higher count determines language

### Limitations

- **Diacritic priority**: Overrides keyword count
- **Small keyword sets**: Only 11 words per language
- **No confidence score**: Binary decision
- **Short text unreliable**: Few words → random result
- **Mixed language**: Picks one, no mixed support

### Usage

- Called on entry title/summary
- Result logged (stdout)
- **Not used** for:
  - Text replacement selection
  - Tag generation
  - Mastodon language parameter
  - Any conditional logic

## Localisation

### Current State

**No localisation support** — All user-facing text is hard-coded in English:

- Log messages (stdout)
- Error messages
- Help text (argparse)

### Hard-coded Strings

| Location | Example |
|----------|---------|
| `main.py` | `'Retrieved ' + str(len(feed.entries)) + ' feed entries!'` |
| `main.py` | `'Failed to create Mastodon app!'` |
| `main.py` | `'Error authenticating with Mastodon: ' + str(e)` |
| `config.py` | No user-facing strings |

### Implications

- Operators must understand English
- No translation mechanism
- No locale-aware formatting (dates, numbers)

## Timezone Handling

### Current State

**No explicit timezone handling** — Mixed naive/aware datetime usage:

- `datetime.now()` — Naive (local time)
- `datetime.strptime()` with `%z` — Aware (UTC offset)
- `datetime.strptime()` without `%z` — Naive
- Comparison: `datetime.now() - entry_date` — May raise `TypeError` in Python 3.11+

### Date Formats Parsed

1. `%a, %d %b %Y %H:%M:%S %z` — RFC 2822 with offset (aware)
2. `%a, %d %b %Y %H:%M:%S %Z` — RFC 2822 with name (naive in Python)
3. `%Y-%m-%dT%H:%M:%S%z` — ISO 8601 with offset (aware)
4. `%Y-%m-%dT%H:%M:%S` — ISO 8601 naive (naive)

### Risk

- Timezone-aware `entry_date` minus naive `datetime.now()` → `TypeError` in Python 3.11+
- No UTC normalisation
- Age calculation may be incorrect across DST boundaries

## Character Encoding

### Assumptions

- **Input**: UTF-8 (RSS feeds, HTML pages, Mastodon API)
- **Processing**: Python 3 native strings (Unicode)
- **Output**: UTF-8 (Mastodon API, stdout)

### Handling

- `feedparser` handles feed encoding detection
- `BeautifulSoup` handles HTML encoding detection
- `requests` handles response encoding detection
- `sqlite3` stores TEXT as UTF-8
- `json` loads/stores UTF-8

### Risks

- No explicit encoding declarations
- Malformed input may cause decode errors
- No fallback encoding strategy

## Related Documentation

- [Application Services](./application-services.md) — Services using HTTP state
- [Integration Models](./integration-models.md) — External service interactions
- [Dependencies](../dependencies.md) — `fake-useragent` dependency
- [Calendar Search Flow](../flows/calendar-search.md) — Language detection in flow