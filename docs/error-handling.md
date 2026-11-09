# Error Handling

## Overview

This document describes the current error handling implementation and defines the target error handling architecture for the mastodon-rss-bot application.

## Current State

### Error Handling Patterns

| Pattern | Location | Description |
|---------|----------|-------------|
| Exception propagation | `main.py`, `config.py`, `database.py` | Most exceptions propagate to top level |
| Try/except with exit | `main.py` (Mastodon auth) | Catch, log, `sys.exit(1)` |
| Try/except with continue | `main.py` (page fetch, media upload) | Catch, log, skip current entry |
| Return value check | `main.py` (app creation) | Check falsy return, exit |
| No handling | `main.py` (feed parse, DB init) | Exceptions propagate, exit 1 |

### Exception Types Encountered

| Exception | Source | Current Handling |
|-----------|--------|------------------|
| `SystemExit` | `argparse` | Exit with usage |
| `FileNotFoundError` | `config.py`, `database.py` | Propagate, exit 1 |
| `json.JSONDecodeError` | `config.py` | Propagate, exit 1 |
| `KeyError` | `config.py` | Propagate, exit 1 |
| `sqlite3.Error` | `database.py` | Propagate, exit 1 |
| `urllib.error.URLError` | `main.py` (page fetch) | Log, continue |
| `requests.RequestException` | `main.py` (media, shortlink) | Log, continue/skip |
| `Mastodon.MastodonError` | `main.py` (API calls) | Log, skip entry/media |
| `ValueError` | `main.py` (date parsing) | Skip entry |
| `TypeError` | `main.py` (datetime comparison) | Propagate, exit 1 |

### Exit Codes

| Code | Condition |
|------|-----------|
| 0 | Success (all entries processed) |
| 1 | Fatal error (config, DB, auth, feed fetch) |

## Target Architecture

### Error Classification

#### 1. Fatal Errors (Process Exit)

Errors that prevent the pipeline from continuing at all.

| Error | Cause | Action |
|-------|-------|--------|
| Config missing/invalid | `config.json` missing, malformed, or incomplete | Exit 1, clear message |
| Database unavailable | `cache.db` permission, corruption, disk full | Exit 1, clear message |
| Mastodon auth failure | Invalid token, instance unreachable | Exit 1, clear message |
| Feed fetch failure | Network error, invalid feed URL | Exit 1, clear message |
| App creation failure | Mastodon API error | Exit 1, clear message |

#### 2. Entry-Level Errors (Skip Entry)

Errors affecting a single entry; pipeline continues with next entry.

| Error | Cause | Action |
|-------|-------|--------|
| Date parse failure | Unrecognised date format | Log WARNING, skip entry |
| Page fetch failure | Network error, timeout, 4xx/5xx | Log WARNING, continue without enrichment |
| Media download failure | Network error, 4xx/5xx | Log WARNING, skip media |
| Media upload failure | Mastodon API error, size limit | Log WARNING, skip media |
| Status post failure | Mastodon API error, rate limit | Log ERROR, skip entry (do not cache) |
| Cache insert failure (duplicate) | Race condition, manual insert | Log ERROR, skip entry |

#### 3. Degraded Operations (Continue with Warning)

Operations that fail but allow partial processing.

| Error | Cause | Action |
|-------|-------|--------|
| Link shortening failure | is.gd unavailable | Log WARNING, use original link |
| Dynamic tags import failure | Module missing/error | Log DEBUG, continue without dynamic tags |
| Text replacements import failure | Module missing/error | Log DEBUG, continue without replacements |
| Language detection failure | Unexpected error | Log DEBUG, default to 'en' |

### Error Handling Principles

1. **Fail fast for fatal errors** — Exit immediately with clear message
2. **Skip gracefully for entry errors** — Log, don't cache, continue
3. **Degrade gracefully for optional features** — Log at DEBUG, continue
4. **Never lose entries silently** — Every skip must be logged at WARNING+
5. **Preserve retry semantics** — Failed posts not cached → retry next run
6. **Mask sensitive data in logs** — No tokens, keys, secrets in output

## Implementation Requirements

### 1. Custom Exception Hierarchy

```python
class MastodonRSSBotError(Exception):
    """Base exception for all application errors."""
    pass

class FatalError(MastodonRSSBotError):
    """Errors that require process exit."""
    pass

class ConfigError(FatalError):
    """Configuration loading errors."""
    pass

class DatabaseError(FatalError):
    """Database connection/operation errors."""
    pass

class AuthenticationError(FatalError):
    """Mastodon authentication errors."""
    pass

class FeedFetchError(FatalError):
    """RSS feed retrieval errors."""
    pass

class EntryError(MastodonRSSBotError):
    """Errors affecting a single entry."""
    pass

class DateParseError(EntryError):
    """Entry date parsing failure."""
    pass

class PageFetchError(EntryError):
    """Linked page retrieval failure."""
    pass

class MediaError(EntryError):
    """Media download/upload failure."""
    pass

class PostError(EntryError):
    """Status posting failure."""
    pass

class CacheError(EntryError):
    """Cache operation failure."""
    pass
```

### 2. Error Handling in Main Pipeline

```python
def main():
    run_id = generate_run_id()
    logger = get_logger(__name__, run_id=run_id)

    try:
        args = parse_args()
        logger.info("Starting pipeline", context={"run_id": run_id, "args": sanitize_args(args)})

        # Fatal error zone - any exception exits
        config = load_config()
        db = init_database()
        mastodon = authenticate_mastodon(args)
        feed = fetch_feed(args.rss)

        # Entry processing zone - errors skip entry
        for entry in reversed(feed.entries):
            try:
                process_entry(entry, args, mastodon, db, config)
            except EntryError as e:
                logger.warning("Entry skipped", context={
                    "run_id": run_id,
                    "entry_hash": getattr(e, 'entry_hash', None),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_action": "entry_skipped"
                })
                continue
            except Exception as e:
                logger.error("Unexpected entry error", context={
                    "run_id": run_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "recovery_action": "entry_skipped"
                }, exc_info=True)
                continue

    except FatalError as e:
        logger.critical("Fatal error", context={
            "run_id": run_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "recovery_action": "process_exit"
        })
        sys.exit(1)
    except Exception as e:
        logger.critical("Unexpected fatal error", context={
            "run_id": run_id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "recovery_action": "process_exit"
        }, exc_info=True)
        sys.exit(1)
```

### 3. Retry Logic (Future Enhancement)

For transient errors (network, rate limits):

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((requests.RequestException, MastodonError)),
    before_sleep=log_retry_attempt
)
def upload_media(mastodon, content, mime_type):
    return mastodon.media_post(content, mime_type=mime_type)
```

### 4. Circuit Breaker (Future Enhancement)

For external services (Mastodon, is.gd, ShrinkMe):

```python
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=(MastodonError, requests.RequestException)
)

@circuit_breaker
def post_status(mastodon, status, media_ids):
    return mastodon.status_post(status=status, media_ids=media_ids)
```

## Error Messages

### User-Facing Messages (stdout/stderr)

| Scenario | Message | Stream |
|----------|---------|--------|
| Config missing | `Configuration file not found. Run with --help for usage.` | stderr |
| Config invalid | `Invalid configuration: <details>` | stderr |
| DB error | `Database error: <details>` | stderr |
| Auth failure | `Authentication failed: <details>` | stderr |
| Feed fetch failure | `Failed to fetch feed: <details>` | stderr |
| Entry skipped (date) | `Skipping entry (unparseable date): <title>` | stdout |
| Entry skipped (page) | `Failed to fetch page for <title>, continuing without enrichment` | stdout |
| Media skipped | `Failed to upload media <url>: <error>` | stdout |
| Post failed | `Failed to post entry <title>: <error>` | stderr |
| Success | `Posted entry: <title>` | stdout |

### Structured Log Context (JSON)

See [Logging](../logging.md) for full structured logging specification.

## Testing Error Handling

### Unit Test Scenarios

| Test | Input | Expected |
|------|-------|----------|
| Config missing | No config.json | ConfigError raised |
| Config malformed | Invalid JSON | ConfigError raised |
| Config incomplete | Missing keys | ConfigError raised |
| DB permission denied | Read-only cache.db | DatabaseError raised |
| Auth invalid token | Bad access_token | AuthenticationError raised |
| Feed network error | Unreachable URL | FeedFetchError raised |
| Date unparseable | Unknown format | DateParseError raised, entry skipped |
| Page fetch 404 | Non-existent URL | PageFetchError raised, entry continues |
| Media upload fail | Mastodon 500 | MediaError raised, media skipped |
| Post fail | Mastodon 401 | PostError raised, entry skipped, not cached |
| Cache duplicate | Manual insert | CacheError raised, entry skipped |

### Integration Test Scenarios

| Test | Setup | Expected |
|------|-------|----------|
| Full pipeline success | Valid config, feed, auth | Exit 0, entries posted, cached |
| Partial failure | 1 of 5 entries fails post | Exit 0, 4 posted, 1 skipped, 4 cached |
| Fatal mid-run | DB corruption after 3 entries | Exit 1, 3 cached, clear error |
| Rate limit | Mastodon 429 on post | Entry skipped, not cached, retry next run |

## Migration Checklist

- [ ] Define custom exception hierarchy
- [ ] Replace bare `except:` with specific exceptions
- [ ] Add structured error logging
- [ ] Implement fatal vs entry error distinction
- [ ] Add retry logic for transient errors
- [ ] Add circuit breaker for external services
- [ ] Mask sensitive data in error messages
- [ ] Add unit tests for all error paths
- [ ] Add integration tests for failure scenarios
- [ ] Document error codes and remediation

## Related Documentation

- [Logging](../logging.md) — Structured error logging
- [Security](../security.md) — Sensitive data in errors
- [API Reference: Main Pipeline](../api-reference/main-pipeline.md) — Error handling call sites
- [Testing](../testing.md) — Error handling test strategy
- [Troubleshooting](../troubleshooting.md) — Operator error resolution