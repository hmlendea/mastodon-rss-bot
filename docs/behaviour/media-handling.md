# Media Handling Behaviour

## Overview

This document describes the observable behavior of media collection, download, upload, and attachment in mastodon-rss-bot.

## Media Sources

Media URLs are collected from multiple sources, in priority order:

```
┌─────────────────────────────────────────────────────────────┐
│                    Media Collection                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Twitter/X → Nitter                                       │
│     └── Parse Nitter page for images/videos                 │
│                                                              │
│  2. Reddit                                                   │
│     └── Parse Reddit page/JSON for media                    │
│                                                              │
│  3. OpenGraph                                                │
│     └── <meta property="og:image"> from linked page         │
│                                                              │
│  4. RSS Enclosures                                           │
│     └── <enclosure> tags in feed entry                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Source 1: Twitter/X via Nitter

**Trigger**: Entry content or link contains `twitter.com` or `x.com` URL.

**Behavior**:
1. URL transformed to Nitter (if privacy frontends enabled)
2. Nitter page fetched
3. HTML parsed for media URLs
4. Image/video URLs extracted

**Observable**:
- HTTP GET to Nitter URL
- BeautifulSoup parsing
- Media URLs collected from page

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Nitter down | Fetch fails, no media from this source |
| Nitter blocks bot | 403, no media |
| Tweet deleted | Nitter error, no media |
| Tweet is video only | Video URL extracted |
| Tweet has multiple images | All image URLs extracted |

### Source 2: Reddit

**Trigger**: Entry content or link contains `reddit.com` URL.

**Behavior**:
1. URL transformed to Redlib (if privacy frontends enabled)
2. Reddit page or JSON API fetched
3. Media URLs extracted

**Observable**:
- HTTP GET to Reddit/Redlib URL
- JSON or HTML parsing
- Media URLs collected

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Reddit blocks bot | 403, no media |
| Post is text-only | No media |
| Post is gallery | Multiple images extracted |
| Post is video | Video URL extracted |
| Redlib instance down | Fetch fails, no media |

### Source 3: OpenGraph

**Trigger**: Linked page has `<meta property="og:image">`.

**Behavior**:
1. Linked page fetched (already done for title extraction)
2. HTML parsed for og:image meta tag
3. Image URL extracted

**Observable**:
- Reuses page HTML from title extraction (no extra fetch)
- BeautifulSoup meta tag parsing
- Single image URL extracted

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| No og:image | No media from this source |
| Multiple og:image | First one used |
| Relative URL | Resolved against page URL |
| og:image is SVG | May not be supported by Mastodon |

### Source 4: RSS Enclosures

**Trigger**: Feed entry has `<enclosure>` tags.

**Behavior**:
1. feedparser parses enclosures
2. Enclosure URLs extracted
3. Type checked (image, audio, video)

**Observable**:
- `entry.enclosures` list from feedparser
- URLs extracted from `enclosure.url` or `enclosure.href`
- MIME type from `enclosure.type`

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| No enclosures | No media from this source |
| Multiple enclosures | All extracted |
| Non-media enclosure | May be skipped or fail |
| Enclosure URL relative | May fail (no resolution) |

## Media Download

**Behavior**: Each collected media URL is downloaded to a local temp file.

**Observable**:
- HTTP GET to media URL
- User-Agent: rotating (fake-useragent)
- File saved to local path
- File extension from URL or Content-Type

**Library**: requests

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Download fails | Undefined (see AMB-013) |
| Timeout | No timeout set, may hang |
| Large file | Downloaded fully to disk |
| Redirect | Followed by requests |
| 403 Forbidden | Download fails |
| Rate limited | Download fails |

**File Naming**:
- Temp file in working directory
- Name derived from URL or hash
- Extension from URL or Content-Type

## Media Upload

**Behavior**: Each downloaded file is uploaded to Mastodon as media attachment.

**Observable**:
- `mastodon.media_post()` called per file
- Returns media object with ID
- Media ID collected for status post

**Library**: Mastodon.py

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Upload fails | Undefined |
| File too large | Mastodon rejects (16MB image, 40MB video) |
| Unsupported format | Mastodon rejects |
| Rate limited | Exception, run crashes |
| >4 media items | Undefined (see AMB-003) |

**Mastodon Media Limits**:
| Type | Max Size | Max Dimensions |
|------|----------|----------------|
| Image | 16 MB | 4096×4096 |
| GIF | 8 MB | — |
| Video | 40 MB | 2:30 duration |
| Audio | 40 MB | — |

## Media Attachment

**Behavior**: Collected media IDs passed to status post.

**Observable**:
- `mastodon.status_post(status=text, media_ids=[...])` called
- Media IDs in order of collection
- Max 4 media IDs (Mastodon limit)

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| 0 media | Status posted without media_ids |
| 1-4 media | All attached |
| >4 media | Undefined (see AMB-003) |

## Temp File Cleanup

**Behavior**: Local media files deleted after upload.

**Observable**:
- `os.remove()` called per temp file
- Files removed after successful upload
- Files may remain if upload fails

**Edge Cases**:
| Scenario | Behavior |
|----------|----------|
| Upload succeeds | File deleted |
| Upload fails | File may remain (orphaned) |
| Process crashes | Files remain (orphaned) |
| Permission error | Deletion fails, file remains |

## Complete Media Flow

```
┌─────────────┐
│  Entry      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Collect URLs│  (Twitter→Nitter, Reddit, OG, Enclosures)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Download   │  (requests → local temp file)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Upload    │  (Mastodon.media_post → media ID)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Delete    │  (os.remove temp file)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Attach to  │  (status_post with media_ids)
│   Status    │
└─────────────┘
```

## Observable Behavior Summary

| Property | Value |
|----------|-------|
| **Max media per post** | 4 (Mastodon limit) |
| **Download timeout** | None |
| **Upload timeout** | Library default |
| **Temp file location** | Working directory |
| **Temp file cleanup** | After upload (best effort) |
| **Alt text** | Not set |
| **Media description** | Not set |
| **Sensitive media flag** | Not set |

## Edge Cases and Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Nitter/Redlib outage | No media from Twitter/Reddit | Disable privacy frontends |
| Media download hang | Run stalls | No timeout (known issue) |
| Orphaned temp files | Disk usage grows | Manual cleanup |
| >4 media items | Post may fail | Limit collection to 4 |
| Large media upload | Mastodon rejects | Pre-check file size |
| Unsupported format | Upload fails | Filter by MIME type |

## Related Documentation

- [Entry Processing](./entry-processing.md) — Media in entry context
- [Integrations](./integrations.md) — Media source details
- [Ambiguities](./ambiguities-and-open-questions.md) — Undefined behaviors
- [Error Handling](../error-handling.md) — Failure behavior
- [State and Persistence](../state-and-persistence.md) — Temp file lifecycle