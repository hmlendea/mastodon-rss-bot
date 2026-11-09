# Application Services

## Overview

This document describes the core business logic services implemented in `main.py`: deduplication, age filtering, content enrichment, media handling, link processing, text transformation, and status posting.

## Service Inventory

| Service | Location | Input | Output | Side Effects |
|---------|----------|-------|--------|--------------|
| Identity Hashing | `main.py` | Entry title, link, published | MD5 hex digest | None |
| Deduplication | `database.py` | Entry hash | Cached row or None | None (read-only) |
| Age Filtering | `main.py` | Published date, days_to_check | Boolean (pass/fail) | None |
| Title Extraction | `main.py` | HTML content, feed title | Extracted title | None |
| Ad Filtering | `main.py` | Title string | Boolean (pass/fail) | None |
| Media Collection | `main.py` | Entry link, HTML, enclosures | List of media URLs | HTTP requests |
| Media Upload | `main.py` | Media URL | Media ID | Mastodon API call |
| Link Processing | `main.py` | Original link | Processed link | HTTP requests (shortlink) |
| Author Extraction | `main.py` | Feed entry author | Formatted author string | None |
| Tag Construction | `main.py` | Feed tags, CLI tags, dynamic tags | Tags string | None |
| Language Detection | `utils.py` | Text string | Language code ('ro'/'en') | None |
| Text Replacement | `main.py` + `text_replacements.py` | Status text | Modified status text | None |
| Status Assembly | `main.py` | All components | Final status string | None |
| Character Truncation | `main.py` | Status string | Truncated status (≤500 chars) | None |
| Status Posting | `main.py` | Status, media_ids | Posted status | Mastodon API call |
| Cache Persistence | `database.py` | Entry fields | Inserted row | SQLite write |

## Identity Hashing

### Purpose

Generate a stable, unique identifier for each feed entry to support deduplication.

### Algorithm

```python
entry_hash = hashlib.md5(
    (feed_entry.title + feed_entry.link + feed_entry.published).encode()
).hexdigest()
```

### Properties

- **Input**: Concatenation of title, link, published (no separator)
- **Output**: 32-character hexadecimal MD5 digest
- **Deterministic**: Same input → same hash
- **Collision risk**: MD5 is cryptographically broken but adequate for deduplication
- **Sensitivity**: Any field change → different hash → re-posting

### Limitations

- No separator between fields → potential ambiguity (e.g., title ending where link begins)
- MD5 not collision-resistant for adversarial inputs
- No versioning — hash algorithm change invalidates entire cache

## Deduplication

### Purpose

Prevent re-posting of already-posted entries.

### Implementation (`database.py:get_last_entry_posted()`)

```python
def get_last_entry_posted(db, entry_hash):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM entries WHERE entry_hash = ?", (entry_hash,))
    return cursor.fetchone()
```

### Behavior

- **Cache hit**: Entry exists → skip processing
- **Cache miss**: Entry new → proceed to enrichment
- **Append-only**: No UPDATE, no DELETE, no TTL, no eviction

### Limitations

- Cache grows unbounded
- No cleanup mechanism
- No deduplication across different feeds (hash includes title+link+published)

## Age Filtering

### Purpose

Skip entries older than the configured window (`--days-to-check`).

### Date Parsing

Tried in order:
1. `%a, %d %b %Y %H:%M:%S %z` — RFC 2822 with timezone
2. `%a, %d %b %Y %H:%M:%S %Z` — RFC 2822 with TZ name
3. `%Y-%m-%dT%H:%M:%S%z` — ISO 8601 with timezone
4. `%Y-%m-%dT%H:%M:%S` — ISO 8601 naive

### Age Calculation

```python
age = datetime.now() - entry_date
if age > timedelta(days=days_to_check):
    continue  # Skip
```

### Limitations

- `datetime.now()` is naive; timezone-aware `entry_date` may cause `TypeError` in Python 3.11+
- All formats failing → entry skipped silently
- No logging of skipped entries

## Title Extraction

### Purpose

Extract the best available title from the linked page.

### Priority Order

1. **OpenGraph**: `<meta property="og:title" content="...">`
2. **HTML title**: `<title>...</title>`
3. **Feed title**: `feed_entry.title` (fallback)

### Implementation

```python
og_title = soup.find('meta', property='og:title')
if og_title and og_title.get('content'):
    title = og_title['content']
elif soup.title and soup.title.string:
    title = soup.title.string
else:
    title = feed_entry.title
```

### Cleaning

- HTML entities decoded (via BeautifulSoup)
- Whitespace normalised
- Ad filter applied (see below)

## Ad Filtering

### Purpose

Skip entries whose titles indicate advertisements.

### Implementation

```python
if 'ad' in title.lower():
    continue  # Skip entry
```

### Limitations

- Substring match → false positives (e.g., "Adelaide", "loading", "adobe")
- Case-insensitive but not word-boundary aware
- No configuration option to disable

## Media Collection

### Purpose

Gather all media URLs associated with an entry for upload to Mastodon.

### Sources (Priority Order)

#### 1. Twitter/X Media (via Nitter)

**Trigger**: Entry link contains `twitter.com` or `x.com`

**Process**:
1. Extract tweet ID and username from URL
2. Construct Nitter URL: `https://nitter.unixfox.eu/<username>/status/<tweet_id>`
3. Fetch Nitter page HTML
4. Parse media URLs from Nitter HTML
5. Rewrite `pbs.twimg.com` → `nitter.unixfox.eu/pic/`

**Hard-coded**: Nitter instance `nitter.unixfox.eu`

#### 2. Reddit Media

**Trigger**: Entry link contains `reddit.com`

**Process**:
1. Append `.json` to Reddit URL
2. Fetch JSON response
3. Parse post data for media URLs
4. Extract image/video URLs

#### 3. OpenGraph Images

**Trigger**: Linked page fetched successfully

**Process**:
1. Parse `<meta property="og:image" content="...">`
2. Extract image URL
3. Add to media list

#### 4. RSS Enclosures

**Trigger**: `feed_entry.enclosures` exists

**Process**:
1. Iterate `feed_entry.enclosures`
2. Extract `enclosure.href` or `enclosure.url`
3. Add to media list

### Media Download

```python
response = requests.get(media_url, headers={'User-Agent': ua.random})
media_content = response.content
```

### Media Upload

```python
media_response = mastodon_api.media_post(
    media_content,
    mime_type=detected_mime_type
)
media_ids.append(media_response['id'])
```

### MIME Type Detection

- Based on URL file extension
- Default: `image/jpeg`

### Limitations

- No media size limit check before upload
- No media count limit (Mastodon allows max 4 media per status)
- No video duration check
- Twitter/Nitter rewriting is fragile (Nitter instances change)
- Reddit JSON API may require authentication for some content

## Link Processing

### Purpose

Transform the entry link through optional stages before inclusion in the status.

### Pipeline

```
Original Link
    ↓
[USE_SHORTLINK=true] → is.gd shortening
    ↓
[USE_PRIVACY_FRONTENDS=true] → Domain replacement
    ↓
Link Cleanup → Tracking parameter removal
    ↓
[MONETISE_LINKS=true] → ShrinkMe.io wrapping
    ↓
Processed Link
```

### Shortlink (`USE_SHORTLINK`)

```python
shortened = requests.get(
    'https://is.gd/create.php?format=simple&url=' + url
).text
```

**Service**: is.gd (hard-coded)

### Privacy Frontends (`USE_PRIVACY_FRONTENDS`)

Hard-coded domain replacements:

| Original | Replacement |
|----------|-------------|
| `old.reddit.com` | `reddit.com` |
| `reddit.com` | `libreddit.kavin.rocks` |
| `twitter.com` | `nitter.net` |
| `youtube.com` | `yewtu.be` |

### Link Cleanup

Regex-based removal of tracking parameters:
- `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`
- `fbclid`, `gclid`
- Other tracking query strings

### Monetisation (`MONETISE_LINKS`)

```python
monetised = (
    'https://shrinkme.io/st?api='
    '81ad7e29077269bcae6dc1773d87abbabeaa9aa8'
    '&url=' + urllib.parse.quote(link)
)
```

**Service**: ShrinkMe.io (hard-coded)
**API Key**: Embedded in source code

## Author Extraction

### Purpose

Include entry author in status when `INCLUDE_AUTHOR=true`.

### Process

1. Extract `feed_entry.author`
2. Clean HTML entities
3. Format: `" by " + author`
4. Append to status text

## Tag Construction

### Purpose

Build hashtag string from multiple sources.

### Sources

1. **Feed tags**: `feed_entry.tags` → extract `term` field
2. **CLI tags**: `--tags-to-add` argument (comma-separated)
3. **Dynamic tags**: `dynamic_tags.py` module (optional)

### Processing

- Strip `#` prefix if present
- Remove spaces and special characters
- Prefix with `#`
- Join with spaces

### Dynamic Tags Loading

```python
dynamic_tags = utils.try_import('dynamic_tags')
if dynamic_tags:
    # Call module function to get additional tags
```

## Language Detection (`utils.py:detect_language()`)

### Purpose

Detect whether entry content is Romanian or English.

### Algorithm

1. Check for Romanian diacritics (ă, â, î, ș, ț)
2. Count Romanian keywords in text
3. Count English keywords in text
4. Return `'ro'` or `'en'` based on counts

### Usage

- Logged for debugging
- May influence text replacements (not currently implemented)

## Text Replacement

### Purpose

Apply configurable regex-based text transformations.

### Loading

```python
text_replacements = utils.try_import('text_replacements')
```

### Interface

Module-level dictionary or list of `(pattern, replacement)` tuples.

### Application

Regex substitution on status text before posting.

## Status Assembly

### Components (Order)

1. Title (extracted, cleaned)
2. Author string (if `INCLUDE_AUTHOR`)
3. Link (processed, if `INCLUDE_LINK`)
4. Tags string
5. Summary/excerpt (if configured)

### Assembly

Concatenated with newlines and spaces.

## Character Truncation

### Limit

500 characters (Mastodon status limit)

### Implementation

```python
if len(status) > 500:
    status = status[:500]
```

### Limitations

- Hard truncation — may cut mid-word, mid-URL, mid-tag
- No word-boundary awareness
- No ellipsis appended
- No warning logged

## Status Posting

### Implementation

```python
mastodon_api.status_post(
    status=status_text,
    media_ids=media_ids
)
```

### Failure Handling

- Exception → log error, skip entry
- Entry NOT cached (will retry next run)
- Loop continues to next entry

## Cache Persistence

### Implementation (`database.py:save_posted_entry()`)

```python
def save_posted_entry(db, entry_hash, entry_title, entry_link, entry_published, entry_author):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO entries (entry_hash, entry_title, entry_link, entry_published, entry_author) VALUES (?, ?, ?, ?, ?)",
        (entry_hash, entry_title, entry_link, entry_published, entry_author)
    )
    db.commit()
```

### Behavior

- INSERT only — no conflict resolution
- Duplicate hash → `sqlite3.IntegrityError` (primary key violation)
- No UPDATE, no DELETE

## Related Documentation

- [Host and Composition](./host-and-composition.md) — Module composition
- [Integration Models](./integration-models.md) — External service interactions
- [Calendar Search Flow](../flows/calendar-search.md) — Preceding flow
- [Detail Mutation Flow](../flows/detail-mutation.md) — This flow in sequence diagram form
- [Configuration](../configuration.md) — Config keys controlling services