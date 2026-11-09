# Ambiguities and Open Questions

## Overview

This document catalogues ambiguities in the mastodon-rss-bot codebase, unresolved design questions, and areas requiring clarification. Each item includes the ambiguity, its impact, and recommended resolution.

## Ambiguities

### AMB-001: Entry Identity Stability

**Ambiguity**: The MD5 hash uses `entry.title + entry.link + entry.published`. If any of these change in the feed, the entry is treated as new.

**Questions**:
- What happens when a feed updates the title of an already-posted entry?
- What happens when `published` date format changes?
- Should identity be based on a stable feed GUID instead?

**Impact**:
- Title change → duplicate post (different hash)
- Date format change → duplicate post
- Feed migration → all entries re-posted

**Recommendation**: Prefer feed-provided `entry.id` or `entry.guid` when available; fall back to hash.

**Resolution Status**: Open

---

### AMB-002: Age Filter Boundary

**Ambiguity**: The `--days-to-check` filter compares entry publication date to current time. The exact comparison operator (>=, >, <=) and timezone handling are not documented.

**Questions**:
- Is the boundary inclusive or exclusive?
- What timezone is used (UTC, local)?
- How are entries with missing/invalid dates handled?

**Impact**:
- Entries exactly at boundary may be inconsistently included/excluded
- Timezone mismatch may skip valid entries
- Missing dates may crash or be silently skipped

**Recommendation**: Document exact comparison, use UTC, handle missing dates explicitly.

**Resolution Status**: Open

---

### AMB-003: Media Limit Enforcement

**Ambiguity**: Mastodon allows max 4 media attachments per status. The code collects media but the enforcement point is unclear.

**Questions**:
- What happens when >4 media items are collected?
- Are they silently dropped, or does the post fail?
- Is there a priority order for which 4 are kept?

**Impact**:
- Posts may fail with API error if >4 media
- Or excess media silently ignored
- No user feedback on dropped media

**Recommendation**: Explicitly limit to 4, log dropped media, document priority order.

**Resolution Status**: Open

---

### AMB-004: Character Limit Truncation Point

**Ambiguity**: Text is truncated to 500 characters, but the truncation point relative to links, tags, and author is unclear.

**Questions**:
- Is truncation applied before or after link processing?
- Are tags included in the 500-char budget?
- Is the link always preserved even if truncation cuts it?

**Impact**:
- Links may be truncated (broken)
- Tags may be cut off
- Author attribution may be lost

**Recommendation**: Define truncation order: content → link → tags → author. Ensure link is never truncated.

**Resolution Status**: Open

---

### AMB-005: Privacy Frontend Fallback

**Ambiguity**: When a privacy frontend is unavailable, the behavior is undefined.

**Questions**:
- Does the code fall back to the original URL?
- Does it skip the link entirely?
- Does it try the next frontend in a list?

**Impact**:
- Broken links if frontend down
- Lost attribution if link skipped
- No visibility into frontend failures

**Recommendation**: Implement fallback chain: frontend → original URL. Log fallback events.

**Resolution Status**: Open

---

### AMB-006: ShrinkMe Failure Handling

**Ambiguity**: The ShrinkMe API key is hard-coded. If the service is down or the key is invalid, behavior is undefined.

**Questions**:
- Does shortlink failure abort the post?
- Does it fall back to the original URL?
- Is the failure logged?

**Impact**:
- Posts may fail due to shortener outage
- Or original URL used silently
- No visibility into shortener health

**Recommendation**: Fall back to original URL on shortener failure. Log the fallback. Make API key configurable.

**Resolution Status**: Open

---

### AMB-007: Feed Parse Failure Behavior

**Ambiguity**: If the RSS feed is malformed or empty, the behavior is not documented.

**Questions**:
- Does feedparser raise an exception?
- Does it return empty entries list?
- Does the bot exit with error or success?

**Impact**:
- Silent success on empty feed (no posts, exit 0)
- Or crash with unhandled exception
- Monitoring cannot distinguish "no new entries" from "feed broken"

**Recommendation**: Distinguish empty feed (success, 0 entries) from parse failure (error, non-zero exit). Log feed status.

**Resolution Status**: Open

---

### AMB-008: Mastodon Rate Limit Handling

**Ambiguity**: The code does not check Mastodon rate limit headers. Behavior when rate limited is undefined.

**Questions**:
- Does Mastodon.py raise on 429?
- Does the bot retry?
- Does it back off?

**Impact**:
- Large feeds may hit rate limits
- Posts fail mid-run
- Remaining entries not processed

**Recommendation**: Check rate limit headers, implement backoff, log rate limit events.

**Resolution Status**: Open

---

### AMB-009: Cache Cleanup Policy

**Ambiguity**: The cache grows unboundedly. No cleanup policy exists.

**Questions**:
- Should old entries be deleted after N days?
- Should the cache be archived?
- Is there a size limit?

**Impact**:
- Cache grows indefinitely (slow, but unbounded)
- No data retention policy
- Compliance concerns (GDPR right to erasure)

**Recommendation**: Implement periodic cleanup (e.g., delete entries older than 90 days). Document retention policy.

**Resolution Status**: Open

---

### AMB-010: Multiple Instance Support

**Ambiguity**: The bot posts to one instance per run. Behavior with multiple instances is undefined.

**Questions**:
- Can one bot post to multiple instances?
- Are app credentials per-instance?
- Is the cache shared across instances?

**Impact**:
- Cross-posting requires multiple runs
- Cache key includes instance? (No — only feed URL + entry link)
- Same entry may post to multiple instances (by design or bug?)

**Recommendation**: Document single-instance design. If multi-instance needed, add instance to cache key.

**Resolution Status**: Open

---

### AMB-011: Author Attribution Format

**Ambiguity**: When `INCLUDE_AUTHOR` is true, the author is prepended. The exact format is not specified.

**Questions**:
- Format: "Author: Name" or "by Name" or "@Name"?
- Is the author name sanitized?
- What if author is missing?

**Impact**:
- Inconsistent attribution format
- Potential injection if author contains special chars
- Missing author handling undefined

**Recommendation**: Standardize format, sanitize author, handle missing author gracefully.

**Resolution Status**: Open

---

### AMB-012: Tag Deduplication

**Ambiguity**: Tags come from multiple sources (CLI, feed, dynamic). Deduplication behavior is unclear.

**Questions**:
- Are duplicate tags removed?
- Are tags case-normalized?
- Is there a max tag count?

**Impact**:
- Duplicate tags in post (ugly)
- Case variants treated as different tags
- Tag spam if feed has many tags

**Recommendation**: Deduplicate case-insensitively, limit tag count, normalize case.

**Resolution Status**: Open

---

### AMB-013: Media Download Failure

**Ambiguity**: If a media URL fails to download, behavior is undefined.

**Questions**:
- Is the media skipped, or does the entry fail?
- Is the error logged?
- Is there a retry?

**Impact**:
- Post may proceed without media (silent)
- Or entire entry skipped
- No visibility into media failures

**Recommendation**: Skip failed media, log the failure, continue with remaining media.

**Resolution Status**: Open

---

### AMB-014: Linked Page Fetch Timeout

**Ambiguity**: `urllib.request.urlopen()` has no explicit timeout. Default behavior is platform-dependent.

**Questions**:
- What is the default timeout?
- Can a slow page hang the bot indefinitely?
- Is there a retry?

**Impact**:
- Bot may hang on slow/unresponsive pages
- Scheduler interval exceeded
- Subsequent entries not processed

**Recommendation**: Set explicit timeout (e.g., 10s), implement retry with backoff.

**Resolution Status**: Open

---

### AMB-015: Configuration Reload

**Ambiguity**: Configuration is loaded once at module import. Changes to `config.json` require restart.

**Questions**:
- Is hot-reload intended?
- Should config be re-read per run?
- What if config.json is deleted mid-run?

**Impact**:
- Config changes not picked up until restart
- Stale config in long-running processes (if any)
- No config change detection

**Recommendation**: Document that config is read once per process start. Consider per-run reload for future.

**Resolution Status**: Open

---

## Open Questions

### OQ-001: Should the Bot Support Multiple Feeds?

**Question**: Should a single bot instance process multiple RSS feeds?

**Considerations**:
- Current: One feed per run (CLI `--rss` argument)
- Multiple feeds require multiple processes or internal loop
- Cache key includes feed URL (supports multiple feeds)
- Scheduling complexity increases

**Options**:
1. Keep single-feed, run multiple instances (current approach)
2. Add `--rss` as repeatable argument, loop internally
3. Add feed list to config.json

**Recommendation**: Option 1 (current) for simplicity. Document multi-feed pattern.

**Status**: Open

---

### OQ-002: Should Media Be Cached Locally?

**Question**: Should downloaded media be cached to avoid re-downloading on re-runs?

**Considerations**:
- Current: Media downloaded, uploaded, deleted per run
- Re-runs (after crash) re-download media
- Cache would reduce bandwidth and API calls
- Adds disk usage and cleanup complexity

**Options**:
1. No cache (current)
2. Cache with TTL (e.g., 7 days)
3. Cache with size limit

**Recommendation**: Option 1 for simplicity. Add cache if bandwidth becomes concern.

**Status**: Open

---

### OQ-003: Should the Bot Post Edits/Updates?

**Question**: If a feed entry is updated (title/content change), should the bot edit the existing toot?

**Considerations**:
- Current: Entry identity includes title → change = new entry → new post
- Mastodon supports status editing
- Would require storing status_id in cache
- Adds complexity (update vs insert)

**Options**:
1. Treat updated entries as new (current)
2. Edit existing toot (requires status_id storage)
3. Skip updated entries (ignore changes)

**Recommendation**: Option 1 for simplicity. Option 2 if edit support becomes requirement.

**Status**: Open

---

### OQ-004: Should the Bot Support Content Warning?

**Question**: Should sensitive entries be posted with content warning (CW)?

**Considerations**:
- Mastodon supports CW field
- Feeds may mark sensitive content
- No current detection of sensitivity
- Would require feed metadata parsing

**Options**:
1. No CW support (current)
2. CW from feed metadata (if available)
3. CW from config (all posts)
4. CW from keyword detection

**Recommendation**: Option 2 if feeds provide sensitivity metadata. Otherwise Option 1.

**Status**: Open

---

### OQ-005: Should the Bot Support Multiple Languages?

**Question**: Should language detection support more than Romanian and English?

**Considerations**:
- Current: RO/EN keyword-based detection
- Other languages → "und" (undefined)
- Mastodon supports many languages
- Library-based detection (langdetect) adds dependency

**Options**:
1. Keep RO/EN only (current)
2. Add langdetect library
3. Make language configurable (skip detection)

**Recommendation**: Option 3 (configurable language) for predictability. Option 2 if multi-language needed.

**Status**: Open

---

### OQ-006: Should the Bot Have a Dry-Run Mode?

**Question**: Should a `--dry-run` flag preview posts without publishing?

**Considerations**:
- Useful for testing and debugging
- Prevents accidental posts
- Requires skipping Mastodon API calls
- Still fetches pages and processes media

**Options**:
1. No dry-run (current)
2. Add `--dry-run` flag
3. Add `--preview` that prints assembled text

**Recommendation**: Option 2. High value for testing, low implementation cost.

**Status**: Open

---

### OQ-007: Should the Bot Deduplicate Across Feeds?

**Question**: If the same content appears in multiple feeds, should it be posted once?

**Considerations**:
- Current: Cache key is (entry_id, entry_link) — same link in different feeds = same key
- Cross-feed dedup happens implicitly if links match
- Different links to same content = duplicate posts

**Options**:
1. Dedup by link only (current implicit behavior)
2. Dedup by content hash
3. No cross-feed dedup

**Recommendation**: Option 1 (current). Document the behavior.

**Status**: Open

---

### OQ-008: Should the Bot Handle Deleted Feed Entries?

**Question**: If a feed entry is deleted from the source, should the bot delete the toot?

**Considerations**:
- Current: No deletion logic
- Mastodon API supports status deletion
- Would require storing status_id
- Ethical/legal implications of auto-deletion

**Options**:
1. No deletion (current)
2. Delete on feed removal (requires status_id)
3. Warn on feed removal

**Recommendation**: Option 1. Auto-deletion is risky and unexpected.

**Status**: Open

---

## Decision Log

| ID | Type | Status | Priority |
|----|------|--------|----------|
| AMB-001 | Ambiguity | Open | Medium |
| AMB-002 | Ambiguity | Open | Medium |
| AMB-003 | Ambiguity | Open | High |
| AMB-004 | Ambiguity | Open | High |
| AMB-005 | Ambiguity | Open | Medium |
| AMB-006 | Ambiguity | Open | High |
| AMB-007 | Ambiguity | Open | Medium |
| AMB-008 | Ambiguity | Open | High |
| AMB-009 | Ambiguity | Open | Low |
| AMB-010 | Ambiguity | Open | Low |
| AMB-011 | Ambiguity | Open | Low |
| AMB-012 | Ambiguity | Open | Low |
| AMB-013 | Ambiguity | Open | Medium |
| AMB-014 | Ambiguity | Open | High |
| AMB-015 | Ambiguity | Open | Low |
| OQ-001 | Open Question | Open | Medium |
| OQ-002 | Open Question | Open | Low |
| OQ-003 | Open Question | Open | Medium |
| OQ-004 | Open Question | Open | Low |
| OQ-005 | Open Question | Open | Low |
| OQ-006 | Open Question | Open | High |
| OQ-007 | Open Question | Open | Low |
| OQ-008 | Open Question | Open | Low |

## Related Documentation

- [Design Decisions](./design-decisions.md) — Recorded decisions
- [Architecture](./architecture.md) — System context
- [Error Handling](./error-handling.md) — Error behavior
- [Change Guide](./change-guide.md) — Proposing resolutions