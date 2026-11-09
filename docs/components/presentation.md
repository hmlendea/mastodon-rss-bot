# Presentation

## Overview

This document describes the presentation layer of the application: command-line interface, output formatting, logging, and user-facing text.

## Interface Type

**Command-line interface (CLI)** — No GUI, no web interface, no daemon mode.

## Command-Line Interface

### Entry Point

```bash
python main.py [arguments]
```

### Argument Definitions

| Argument | Required | Type | Description |
|----------|----------|------|-------------|
| `--rss` | Yes | String | RSS feed URL |
| `--instance` | Yes | String | Mastodon instance domain |
| `--username` | Yes | String | Mastodon username |
| `--access-token` | Yes | String | Mastodon OAuth access token |
| `--tags-to-add` | No | String | Comma-separated hashtags to add |
| `--days-to-check` | No | Integer | Age window in days |

### Argument Parsing

**Library**: `argparse` (standard library)

**Implementation** (`main.py:parse_args()`):

```python
def parse_args():
    parser = argparse.ArgumentParser(description='Mastodon RSS Bot')
    parser.add_argument('--rss', required=True, help='RSS feed URL')
    parser.add_argument('--instance', required=True, help='Mastodon instance')
    parser.add_argument('--username', required=True, help='Mastodon username')
    parser.add_argument('--access-token', required=True, help='Mastodon access token')
    parser.add_argument('--tags-to-add', required=False, help='Tags to add')
    parser.add_argument('--days-to-check', required=False, type=int, help='Days to check')
    return parser.parse_args()
```

### Usage Examples

```bash
# Basic invocation
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token abc123

# With optional arguments
python main.py \
  --rss https://example.com/feed.xml \
  --instance mastodon.social \
  --username user@example.com \
  --access-token abc123 \
  --tags-to-add "news,tech" \
  --days-to-check 7
```

### Help Output

```
usage: main.py [-h] --rss RSS --instance INSTANCE --username USERNAME
               --access-token ACCESS_TOKEN [--tags-to-add TAGS_TO_ADD]
               [--days-to-check DAYS_TO_CHECK]

Mastodon RSS Bot

options:
  -h, --help            show this help message and exit
  --rss RSS             RSS feed URL
  --instance INSTANCE   Mastodon instance
  --username USERNAME   Mastodon username
  --access-token ACCESS_TOKEN
                        Mastodon access token
  --tags-to-add TAGS_TO_ADD
                        Tags to add
  --days-to-check DAYS_TO_CHECK
                        Days to check
```

## Output Streams

### stdout

**Purpose**: Informational logging
**Content**:
- Entry count retrieved
- Processing progress messages
- Success confirmations
- Language detection results

**Format**: Plain text, no timestamps, no log levels

**Example**:
```
Retrieved 25 feed entries!
Processing entry: Example News Article
Language detected: en
Posted entry: Example News Article
```

### stderr

**Purpose**: Error messages
**Content**:
- Authentication failures
- API errors
- Processing errors

**Format**: Plain text, no timestamps, no log levels

**Example**:
```
Error authenticating with Mastodon: 401 Unauthorized
Failed to create Mastodon app!
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (all entries processed or skipped) |
| 1 | Fatal error (config, DB, auth, feed fetch failure) |

## Logging Model

### Mechanism

**`print()` statements** — No `logging` module, no log levels, no structured logging.

### Characteristics

| Property | Value |
|----------|-------|
| Log levels | None (all messages equal) |
| Timestamps | None |
| Structured format | None (plain text) |
| Log file | None (stdout/stderr only) |
| Rotation | N/A |
| Verbosity control | None |
| Contextual data | Minimal (inline in message) |

### Message Categories

| Category | Stream | Example |
|----------|--------|---------|
| Info | stdout | `Retrieved 25 feed entries!` |
| Progress | stdout | `Processing entry: ...` |
| Success | stdout | `Posted entry: ...` |
| Warning | stdout | `Failed to fetch page, skipping enrichment` |
| Error | stderr | `Error authenticating with Mastodon: ...` |
| Fatal | stderr | `Failed to create Mastodon app!` |

### Limitations

1. **No log levels** — Cannot filter by severity
2. **No timestamps** — Cannot correlate with external events
3. **No structured format** — Cannot parse programmatically
4. **No log file** — Output lost when terminal closes
5. **No rotation** — N/A (no file output)
6. **No verbosity control** — Cannot reduce noise
7. **No context** — Limited entry identification in messages

## User-Facing Text

### Language

All user-facing text is **English** (hard-coded, no localisation).

### Text Inventory

| Message | Location | Stream |
|---------|----------|--------|
| `Retrieved N feed entries!` | `main.py` | stdout |
| `Processing entry: <title>` | `main.py` | stdout |
| `Posted entry: <title>` | `main.py` | stdout |
| `Language detected: <lang>` | `main.py` | stdout |
| `Failed to fetch page, skipping enrichment` | `main.py` | stdout |
| `Error authenticating with Mastodon: <error>` | `main.py` | stderr |
| `Failed to create Mastodon app!` | `main.py` | stderr |
| `Failed to post entry: <error>` | `main.py` | stderr |

### Formatting

- No colour/ANSI codes
- No indentation
- No structured fields
- Plain concatenation with `+` operator

## Configuration Presentation

### Config File

`config.json` — JSON format, human-readable, no comments.

### Sample Config

`sample.config.json` — Template with default values.

### No Interactive Setup

- No wizard
- No prompts
- No validation UI
- Operator edits JSON manually

## Error Presentation

### To Operator

- Plain text error message on stderr
- Process exits with code 1
- No stack trace (except uncaught exceptions)
- No remediation guidance

### To Mastodon

- Status text only (no error indication)
- Failed entries not posted
- No error toot or notification

## Accessibility

### Current State

- **No accessibility features** — CLI only, no screen reader considerations
- **No alternative formats** — No JSON/CSV output option
- **No quiet mode** — Cannot suppress stdout
- **No verbose mode** — Cannot increase detail

### Recommendations

1. Add `--quiet` flag to suppress stdout
2. Add `--verbose` flag for detailed logging
3. Add `--log-file` option for file output
4. Add `--json` output mode for programmatic consumption
5. Use `logging` module with levels

## Related Documentation

- [Host and Composition](./host-and-composition.md) — Process topology
- [Application Services](./application-services.md) — Services producing output
- [Logging](../logging.md) — Logging requirements and recommendations
- [Error Handling](../error-handling.md) — Error presentation details
- [Build and Deployment](../build-and-deployment.md) — CLI invocation in deployment