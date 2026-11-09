# Entry Processing Behaviour

## Overview

This document describes the observable behavior of the entry processing pipeline: how entries are selected, filtered, enriched, and posted.

## Entry Selection

### Feed Fetch

**Behavior**: The bot fetches the RSS/Atom feed specified by `--rss` on every run.

**Observable**:
- HTTP GET to feed URL
- User-Agent: rotating (fake-useragent)
- No conditional GET (no If-Modified-Since, no ETag)
- Full feed downloaded every run

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Feed returns 304 | Not handled (no conditional GET) |
| Feed returns 404 | Exception, run crashes |
| Feed returns 500 | Exception, run crashes |
| Feed returns non-XML | feedparser bozo=1, may parse partially |
| Feed empty | No entries, run exits normally |
| Feed timeout | No timeout, may hang indefinitely |

### Entry Ordering

**Behavior**: Entries are processed in **reverse order** (oldest first).

**Rationale**: Feeds typically list newest first. Reversing ensures oldest unposted entries are posted first, maintaining chronological order in the Mastodon timeline.

**Observable**:
```python
for entry in reversed(feed.entries):
    # process
```

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Feed not sorted by date | Reverse order may not be chronological |
| Entries with same date | Order preserved from feed |
| Single entry | No effect |

## Filtering

### Deduplication Filter

**Behavior**: Before processing, the bot checks if the entry was already posted.

**Identity**: MD5 hash of `entry.title + entry.link + entry.published`.

**Lookup**: `get_last_entry_posted(db, entry_id, entry.link)` — checks composite key `(entry_id, entry_link)`.

**Observable**:
- Cache hit → entry skipped (no output, no post)
- Cache miss → entry processed

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Title changed in feed | Different hash → re-posted (duplicate) |
| Link changed in feed | Different hash → re-posted |
| Published date changed | Different hash → re-posted |
| Same content, different feed | Same link → deduped (if same entry_id) |
| Cache deleted | All entries re-posted (if within age window) |

### Age Filter

**Behavior**: Entries older than `--days-to-check` are skipped.

**Comparison**: Entry publication date vs current time minus N days.

**Observable**:
- Entry within window → processed
- Entry outside window → skipped

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Missing published date | Undefined (see AMB-002) |
| Invalid date format | Parse error, behavior undefined |
| Future-dated entry | Within window, processed |
| Exactly at boundary | Inclusive/exclusive undefined |
| Timezone mismatch | Possible incorrect filtering |

### Maximum Toots Filter

**Behavior**: Processing stops after `MAXIMUM_TOOTS_COUNT` entries are posted.

**Default**: 10 (from config.json).

**Observable**:
- Counter increments per successful post
- When counter reaches limit, loop exits
- Remaining entries not processed (not cached, not posted)

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Limit = 0 | No posts (loop exits immediately) |
| Limit > entries | All entries processed |
| Post fails mid-run | Counter not incremented, next entry attempted |

## Enrichment

### Linked Page Fetch

**Behavior**: For each entry, the bot fetches the linked page (`entry.link`).

**Observable**:
- HTTP GET to entry link
- User-Agent: rotating (fake-useragent)
- No timeout
- HTML decoded as UTF-8 (errors ignored)

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Page returns 404 | Exception, run crashes |
| Page returns 500 | Exception, run crashes |
| Page redirects | Followed by urllib |
| Page requires JS | Static HTML only, no JS execution |
| Page is non-HTML | Parsing may fail, fallback to feed title |
| Page timeout | No timeout, may hang |

### Title Extraction

**Behavior**: Three-tier priority extraction from linked page HTML.

**Priority**:
1. OpenGraph `og:title` meta tag
2. First `<h1>` element
3. `<title>` element

**Observable**:
- Tier 1 match → used, tiers 2-3 skipped
- Tier 1 missing → tier 2 attempted
- Tier 2 missing → tier 3 attempted
- All missing → empty title (fallback to feed title? undefined)

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Multiple og:title | First one used |
| Empty og:title | Falls through to next tier |
| Multiple h1 | First one used |
| Empty h1 | Falls through to next tier |
| No title tag | Empty string |
| HTML entities | Decoded by BeautifulSoup |

### Ad Filter

**Behavior**: Extracted title is checked against ad patterns.

**Observable**:
- Title matching ad pattern → discarded, fallback used
- Title not matching → used as-is

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Ad pattern in legitimate title | False positive, title discarded |
| Ad pattern variations | May not match (pattern list limited) |

## Posting

### Status Assembly

**Behavior**: Final status text assembled from components.

**Order** (typical):
1. Author (if `INCLUDE_AUTHOR`)
2. Title (extracted or feed)
3. Summary/excerpt (if available)
4. Link (if `INCLUDE_LINK`)
5. Tags (CLI + feed + dynamic)

**Observable**:
- Components concatenated with separators
- Total length checked against 500 chars
- Truncated if exceeds limit

### Media Attachment

**Behavior**: Media collected, downloaded, uploaded, attached to status.

**Observable**:
- Media URLs collected from multiple sources
- Each URL downloaded to temp file
- Each file uploaded to Mastodon
- Media IDs collected
- Status posted with media_ids

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| No media found | Status posted without media |
| Media download fails | Undefined (see AMB-013) |
| Media upload fails | Undefined |
| >4 media items | Undefined (see AMB-003) |

### Status Post

**Behavior**: Final status posted via Mastodon API.

**Observable**:
- `mastodon.status_post()` called with text, media_ids, language
- Returns status object with ID and URL
- Status URL cached

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Text > 500 chars | Truncated before posting |
| Rate limited | Exception, run crashes |
| Instance down | Exception, run crashes |
| Duplicate content | Mastodon may reject (spam filter) |

## Cache Update

**Behavior**: After successful post, entry saved to cache.

**Observable**:
- `save_posted_entry()` called with entry details + status URL
- INSERT only (no UPDATE)
- Immediate commit

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Post succeeds, cache INSERT fails | Entry not cached → re-posted next run (duplicate) |
| Post fails | Cache not updated, entry retried next run |
| Cache DB locked | Exception, run crashes |

## Complete Entry Lifecycle

```
┌─────────────┐
│  Feed Entry │
└──────┬──────┘
       │
       ▼
┌─────────────┐    Yes    ┌─────────────┐
│  In Cache?  │──────────▶│    SKIP     │
└──────┬──────┘           └─────────────┘
       │ No
       ▼
┌─────────────┐    No     ┌─────────────┐
│  Within Age │──────────▶│    SKIP     │
│   Window?   │           └─────────────┘
└──────┬──────┘
       │ Yes
       ▼
┌─────────────┐
│  Fetch Page │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Extract Title│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Collect Media│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Assemble   │
│    Text     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Post to    │
│  Mastodon   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Cache Entry│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Next Entry │
└─────────────┘
```

## Related Documentation

- [Pipeline Flow](./flows/startup-and-rendering.md) — Full pipeline flow
- [Data Model](./data-model.md) — Cache schema
- [Ambiguities](./ambiguities-and-open-questions.md) — Undefined behaviors
- [Error Handling](./error-handling.md) — Failure behavior