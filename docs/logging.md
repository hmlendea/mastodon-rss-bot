# Logging

## Overview

This document specifies the logging requirements for the mastodon-rss-bot application. The current implementation uses `print()` statements with no structured logging. This document defines the target logging architecture.

## Current State

| Property | Current Implementation |
|----------|------------------------|
| Mechanism | `print()` to stdout/stderr |
| Log levels | None |
| Timestamps | None |
| Structured format | None |
| Log file | None |
| Rotation | N/A |
| Verbosity control | None |
| Contextual data | Minimal |

## Requirements

### 1. Structured Logging Format

**Requirement**: All log entries MUST be structured JSON with consistent fields.

**Fields**:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "mastodon_rss_bot.main",
  "message": "Retrieved 25 feed entries",
  "context": {
    "entry_count": 25,
    "feed_url": "https://example.com/feed.xml"
  }
}
```

**Mandatory fields**: `timestamp`, `level`, `logger`, `message`
**Optional fields**: `context` (object), `trace_id` (for correlation)

### 2. Log Levels

**Requirement**: Support standard log levels with filtering.

| Level | Numeric | Use Case |
|-------|---------|----------|
| DEBUG | 10 | Detailed diagnostic information |
| INFO | 20 | General operational information |
| WARNING | 30 | Unexpected but handled situations |
| ERROR | 40 | Failed operations (entry skipped) |
| CRITICAL | 50 | Fatal errors (process exit) |

**Default level**: INFO
**Configurable via**: `--log-level` CLI argument or `LOG_LEVEL` env var

### 3. Timestamps

**Requirement**: All log entries MUST include ISO 8601 UTC timestamps with millisecond precision.

**Format**: `YYYY-MM-DDTHH:MM:SS.mmmZ` (e.g., `2024-01-15T10:30:45.123Z`)

**Implementation**: Use `datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'`

### 4. Logger Hierarchy

**Requirement**: Use hierarchical logger names matching module structure.

| Module | Logger Name |
|--------|-------------|
| `main.py` | `mastodon_rss_bot.main` |
| `config.py` | `mastodon_rss_bot.config` |
| `database.py` | `mastodon_rss_bot.database` |
| `utils.py` | `mastodon_rss_bot.utils` |

**Root logger**: `mastodon_rss_bot`

### 5. Contextual Logging

**Requirement**: Include relevant context in structured `context` field.

**Mandatory context per operation**:

| Operation | Context Fields |
|-----------|----------------|
| Feed fetch | `feed_url`, `entry_count` |
| Entry processing | `entry_hash`, `entry_title`, `entry_link` |
| Page fetch | `page_url`, `status_code` |
| Media upload | `media_url`, `media_type`, `media_id` |
| Status post | `status_length`, `media_count`, `toot_id` |
| Cache operation | `entry_hash`, `operation` (lookup/insert) |
| Config load | `config_path`, `keys_loaded` |

### 6. Correlation IDs

**Requirement**: Generate a run ID at startup; include in all log entries.

**Format**: UUID v4 (e.g., `a1b2c3d4-e5f6-7890-abcd-ef1234567890`)

**Field name**: `run_id` in context

**Usage**: Enables filtering all logs from a single pipeline execution.

### 7. Output Destinations

**Requirement**: Support multiple simultaneous outputs.

| Destination | Format | Use Case |
|-------------|--------|----------|
| stdout | JSON lines | Container logging, log aggregation |
| File | JSON lines | Persistent storage, audit trail |
| stderr | Human-readable | Interactive debugging |

**Default**: stdout only (JSON lines)
**Configurable via**: `--log-output` CLI argument (comma-separated: `stdout,file,stderr`)

### 8. Log File Rotation

**Requirement**: When file output enabled, rotate logs.

**Policy**:
- Max file size: 10 MB
- Max files: 5
- Rotation: Size-based with numeric suffixes
- Compression: gzip rotated files

**Implementation**: `logging.handlers.RotatingFileHandler`

### 9. Sensitive Data Masking

**Requirement**: Never log sensitive values in plain text.

**Masked fields**:
- `access_token` → `***MASKED***`
- `api_key` (ShrinkMe) → `***MASKED***`
- `client_secret` → `***MASKED***`
- Any field containing `token`, `secret`, `key`, `password` (case-insensitive)

**Implementation**: Custom `logging.Filter` that redacts sensitive keys from context.

### 10. Performance Logging

**Requirement**: Log timing for key operations.

**Operations to time**:
- Feed fetch and parse
- Linked page fetch
- Media download
- Media upload
- Status post
- Database operations

**Format**: Include `duration_ms` in context.

```json
{
  "message": "Feed fetch completed",
  "context": {
    "feed_url": "https://example.com/feed.xml",
    "duration_ms": 1234,
    "entry_count": 25
  }
}
```

### 11. Error Logging

**Requirement**: Errors MUST include exception details and recovery action.

**Error log format**:
```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "logger": "mastodon_rss_bot.main",
  "message": "Failed to post entry",
  "context": {
    "entry_hash": "abc123...",
    "entry_title": "Example Article",
    "error_type": "MastodonError",
    "error_message": "401 Unauthorized",
    "recovery_action": "entry_skipped_not_cached",
    "stack_trace": "Traceback (most recent call last)..."
  }
}
```

**Mandatory error context**: `error_type`, `error_message`, `recovery_action`

### 12. Configuration

**Requirement**: Logging configuration via CLI and environment.

**CLI Arguments**:
- `--log-level` — DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
- `--log-output` — stdout,file,stderr (default: stdout)
- `--log-file` — Path to log file (default: `logs/mastodon-rss-bot.log`)
- `--log-format` — json,human (default: json)

**Environment Variables**:
- `LOG_LEVEL` — Same as `--log-level`
- `LOG_OUTPUT` — Same as `--log-output`
- `LOG_FILE` — Same as `--log-file`
- `LOG_FORMAT` — Same as `--log-format`

**Precedence**: CLI > Environment > Defaults

## Implementation Plan

### Phase 1: Core Infrastructure

1. Add `logging` module import to all modules
2. Create `mastodon_rss_bot/logging_config.py` with:
   - `configure_logging()` function
   - Custom `JSONFormatter` class
   - `SensitiveDataFilter` class
   - `RunIdFilter` class
2. Modify `main.py` to call `configure_logging()` at startup
3. Replace all `print()` calls with `logger.info()`, `logger.error()`, etc.

### Phase 2: Context Enrichment

1. Add context parameters to all logging calls
2. Implement timing decorators/context managers
3. Add correlation ID generation

### Phase 3: Configuration Integration

1. Add CLI arguments for logging config
2. Add environment variable support
3. Validate configuration

## Migration Checklist

- [ ] Add `logging` imports to all modules
- [ ] Create `logging_config.py`
- [ ] Replace `print()` in `main.py`
- [ ] Replace `print()` in `config.py`
- [ ] Replace `print()` in `database.py`
- [ ] Replace `print()` in `utils.py`
- [ ] Add CLI arguments for logging
- [ ] Add environment variable support
- [ ] Add sensitive data filter
- [ ] Add timing instrumentation
- [ ] Test JSON output parsing
- [ ] Test file rotation
- [ ] Verify no sensitive data in logs

## Related Documentation

- [Error Handling](../error-handling.md) — Error logging details
- [Security](../security.md) — Sensitive data handling
- [Build and Deployment](../build-and-deployment.md) — Logging in deployment
- [API Reference: Main Pipeline](../api-reference/main-pipeline.md) — Logging call sites